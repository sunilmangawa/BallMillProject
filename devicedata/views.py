from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
# from django.contrib.auth.models import User
from django.db.models import Avg
from django.db.models.functions import ExtractDay, ExtractMonth, ExtractYear
from django.utils import timezone

from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from rest_framework import generics, permissions
from django.views import generic, View
# from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from .models import Company, Device, Milldata
from .serializers import CompanySerializer, DeviceSerializer, MilldataSerializer
from .forms import CustomUserCreationForm, EditFeedingForm
from django.http import FileResponse
from reportlab.pdfgen import canvas
from openpyxl import Workbook
from io import BytesIO
from reportlab.lib.pagesizes import letter, landscape, portrait
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import xlsxwriter
# from datetime import datetime
from django.core.paginator import Paginator
import pandas as pd
from datetime import datetime, timedelta, time
from fpdf import FPDF
# import datetime
from .permissions import IsSuperUserOrStaff
from collections import deque
from django.http import JsonResponse
import pytz
import csv
from itertools import chain

class IsSuperUserOrStaff(permissions.BasePermission):
    """
    Custom permission to only allow superusers or staff members to access the create functionality.
    """
    def has_permission(self, request, view):
        if request.method == "POST":
            return request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)
        return True

def home_page_view(request):
    return render(request, 'home.html')

def products(request):
    return render(request, 'products.html')

def about_us(request):
    return render(request, 'about_us.html')

def contact_us(request):
    return render(request, 'contact_us.html')

def terms_and_conditions(request):
    return render(request, 'terms_and_conditions.html')

class MilldataListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MilldataSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        device_id = self.kwargs['device_id']
        return Milldata.objects.filter(device_id=device_id)

    def perform_create(self, serializer):
        device_id = self.kwargs['device_id']
        device = Device.objects.get(id=device_id)

        # Fetch required data from Device model
        initial_hold = device.initial_hold
        circle = device.circle
        feed_time = device.feed_time
        circle_hold = device.circle_hold
        galla_clear_time = device.galla_clear_time
        actual_hold = device.actual_hold
        overload_hold = device.overload_hold

        # Pass the fetched data to the serializer's save method
        serializer.save(
            device=device,
            initial_hold = initial_hold,
            circle = circle,
            feed_time = feed_time,
            circle_hold = circle_hold,
            galla_clear_time = galla_clear_time,
            actual_hold = actual_hold,
            overload_hold = overload_hold,
        )


class DashboardView(generic.TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        companies = Company.objects.filter(owner=user)
        context['companies'] = companies
        context['user'] = user

        # today = timezone.now()
        today = timezone.localtime(timezone.now())
        company_devices_data = []

        # Fetch all devices for the current user's companies in one query
        devices = Device.objects.select_related('company').filter(company__in=companies)

        # Fetch all milldata for the current user's devices in one query
        all_milldata_today = Milldata.objects.filter(device__in=devices, katta_time__date=today.date())
        all_milldata_previous_day = Milldata.objects.filter(device__in=devices, katta_time__date=today.date() - timedelta(days=1))

        now = timezone.localtime(timezone.now())
        today_date = now.date()

        for company in companies:
            devices_data = []
            morning_shift_start_time = company.morning_shift_start_time
            evening_shift_start_time = company.evening_shift_start_time

            morning_start_time = timezone.make_aware(datetime.combine(today_date, morning_shift_start_time))
            evening_start_time = timezone.make_aware(datetime.combine(today_date, evening_shift_start_time))

            for device in devices.filter(company=company):
                device_data = {}
                milldata_today = [data for data in all_milldata_today if data.device_id == device.id]
                total_bags = len(milldata_today)
                adjusted_duration = 0

                for i in range(total_bags):
                    if i == 0:
                        time_diff = 120
                    else:
                        time_diff = (milldata_today[i].katta_time - milldata_today[i - 1].katta_time).total_seconds()
                    if time_diff <= 300:
                        adjusted_duration += time_diff
                    else:
                        adjusted_duration += 120

                avg_time = adjusted_duration / total_bags if total_bags > 0 else 0
                avg_only = (3600/avg_time) if total_bags >0 else 0

                milldata_previous_day = [data for data in all_milldata_previous_day if data.device_id == device.id]

   
                if evening_start_time <= now < (morning_start_time + timedelta(days=1)):# Evening Shift (7:00) to Midnight (12:00)
                    morning_shift_start = morning_start_time
                    morning_shift_end = evening_start_time
                    evening_shift_start = evening_start_time
                    evening_shift_end = now

                    morning_shift_data_today = [data for data in milldata_today if morning_shift_start <= data.katta_time <= morning_shift_end]
                    evening_shift_data_today = [data for data in milldata_today if evening_shift_start <= data.katta_time <= evening_shift_end]
                    morning_shift_data_previous_day = []
                    evening_shift_data_previous_day = []

                elif (evening_start_time - timedelta(days=1)) <= now < morning_start_time: # After 12:00 Midnight to 7:00 Morning Shift
                    morning_shift_start = (morning_start_time - timedelta(days=1))
                    morning_shift_end = (evening_start_time - timedelta(days=1))
                    evening_shift_start = (evening_start_time - timedelta(days=1))
                    evening_shift_end = morning_start_time

                    morning_shift_data_today = []
                    morning_shift_data_previous_day = [data for data in milldata_previous_day if morning_shift_start <= data.katta_time <= morning_shift_end]
                    evening_shift_data_today = []
                    evening_shift_data_previous_day_part1 = [data for data in milldata_previous_day if evening_shift_start <= data.katta_time <= timezone.make_aware(datetime.combine(today_date, time(0, 0)))]
                    evening_shift_data_today_part2 = [data for data in milldata_today if timezone.make_aware(datetime.combine(today_date, time(0, 0))) <= data.katta_time <= morning_start_time]
                    evening_shift_data_previous_day = list(chain(evening_shift_data_previous_day_part1, evening_shift_data_today_part2))

                else:
                    if morning_start_time <= now < evening_start_time: # Morning Shift (7:00) to Evening Shift 
                        morning_shift_start = morning_start_time  # 7:00 AM of  today
                        morning_shift_end = evening_start_time  # 19:00 of today
                        evening_shift_start = (evening_start_time - timedelta(days=1))
                        evening_shift_end = morning_start_time

                        morning_shift_data_today = [data for data in milldata_today if morning_shift_start <= data.katta_time <= morning_shift_end]
                        morning_shift_data_previous_day = []
                        evening_shift_data_today = [data for data in milldata_today if timezone.make_aware(datetime.combine(today_date, time(0, 0))) <= data.katta_time <= morning_shift_start]

                        evening_shift_data_previous_day = [data for data in milldata_previous_day if evening_shift_start <= data.katta_time <= timezone.make_aware(datetime.combine(today_date, time(6, 59)))]
                morning_shift_data = list(chain(morning_shift_data_previous_day, morning_shift_data_today))
                evening_shift_data = list(chain(evening_shift_data_previous_day, evening_shift_data_today))

                morning_total_bags = len(morning_shift_data)
                evening_total_bags = len(evening_shift_data)                
                device_data['morning_shift'] = morning_total_bags
                device_data['evening_shift'] = evening_total_bags
                device_data['device'] = device
                device_data['total_bags'] = total_bags
                device_data['average_time'] = avg_time
                device_data['average_only'] = avg_only
                devices_data.append(device_data)

            company_devices_data.append({'company': company, 'devices_data': devices_data})

        context['company_devices_data'] = company_devices_data
        return context


class CompanyDashboardView(generic.TemplateView):
    template_name = 'company_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company_id = self.kwargs['company_id']
        company = Company.objects.get(pk=company_id)
        context['company'] = company
        devices = Device.objects.filter(company__id=company_id)
        latest_data = []
        for device in devices:
            milldata = Milldata.objects.filter(device=device).order_by('-id').first()
            latest_data.append(milldata)
        context['devices'] = zip(devices, latest_data)
        return context

@login_required
def device_data(request, company_id, device_id):
    device_data  = Milldata.objects.filter(company_id=company_id, device_id=device_id)
    # perform calculations to get average by shift time
    # render the data in a template
    return render(request, 'dashboard.html', {'device_data ': device_data })

@login_required
def profile(request):
    user = request.user
    companies = Company.objects.filter(owner=user)
    context = {'user': user, 'companies': companies}
    return render(request, 'profile.html', context)

class CompanyDetailView(generic.DetailView):
    model = Company
    template_name = 'company_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.get_object()
        devices = Device.objects.filter(company=2)
        latest_data = []
        
        milldata = Milldata.objects.filter(device=3).order_by('-id').first()
        #latest_data.append(milldata)
        
        latest_data.append(milldata)
        context['devices'] = zip(devices, latest_data)
        return context

class EditFeedingView(LoginRequiredMixin, generic.UpdateView):
    model = Device
    form_class = EditFeedingForm
    template_name = "edit_feeding.html"

    def get_queryset(self):
        # Ensure the user can only edit devices that belong to their company
        return Device.objects.filter(company__owner=self.request.user)  

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()

        # Get the company's primary key from the device instance
        company_pk = self.object.company.pk

        # Redirect to the dashboard view with the primary key
        return HttpResponseRedirect(reverse('dashboard', args=[company_pk]))

class DeviceDetailView(generic.DetailView):
    model = Device
    template_name = 'device_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # New code starts here
        # Add the following lines to get the company devices data from DashboardView
        dashboard_view = DashboardView()
        dashboard_view.request = self.request
        dashboard_context = dashboard_view.get_context_data()
        context['company_devices_data'] = dashboard_context['company_devices_data']
        print("Company devices data:", context['company_devices_data'])
        # New code Ends here

        device = self.object
        L5 = deque(maxlen=5)
        L10 = deque(maxlen=10)
        L15 = deque(maxlen=15)
        L20 = deque(maxlen=20)
        # Get today's date in local timezone
        today = timezone.localtime(timezone.now())
        start_date, end_date, milldata_today, total_bags, average_time = get_device_data(self.request, device) #new

        # Get Milldata for today
        machine_on_time = []
        machine_off_time = []
        milldata_with_avg = []

        # To show Total Bags Today, Average Time Today, Average Bags per Hour, Predicted Bags Today's values at Bottom of device_detail.html under Milldata Heading
        for i in range(1, total_bags+1):
            current_data = milldata_today[i-1]
            reversed_index = total_bags - i + 1  # Add this line
            if i <= 1:
                time_diff = 120.00
                fill_time = 120.00
            else:
                time_diff = round((current_data.katta_time - milldata_today[i - 2].katta_time).total_seconds(),2)
                fill_time = round((current_data.katta_time - milldata_today[i - 2].katta_time).total_seconds(),2)
            
            if time_diff > 300:
                adjusted_time_diff = time_diff - 120
                machine_off_time.append(adjusted_time_diff)
                time_diff = 120
                machine_on_time.append(time_diff)
            else:
                machine_on_time.append(time_diff)
            if i ==1:
                total_time = 120
            else:
                total_time = (current_data.katta_time - milldata_today[0].katta_time).total_seconds()+120
            
            # Update lists
            L5.append(time_diff)
            L10.append(time_diff)
            L15.append(time_diff)
            L20.append(time_diff)

            total_adjusted_time = 0
            for j in range(i):
                if j==0:
                    time_diff=120
                else:
                    time_diff = (milldata_today[j].katta_time - milldata_today[j - 1].katta_time).total_seconds()
                if time_diff > 300:
                    adjusted_time_diff = time_diff - 120
                    total_adjusted_time += adjusted_time_diff

            adjusted_total_time = total_time - total_adjusted_time
            if adjusted_total_time > 0:
                if i==1:
                    avg_with_bag = (i / 120) * 3600
                else:
                    avg_with_bag = (i / adjusted_total_time) * 3600
            else:
                avg_with_bag = 0

            current_data.avg_per_hour = avg_with_bag

            current_data.fill_time = fill_time  # Add time_diff value to current_data objects
            # current_data.fill_time = time_diff  # Add time_diff value to current_data object
            current_data.reversed_index = reversed_index
            #milldata_with_avg.append(current_data)
            milldata_with_avg.insert(0, current_data)  # Insert at the beginning of the list
        
        # To correctly calulate  Average Time Today, Average Bags per Hour, Predicted Bags Today's values shown at Top of device_detail.html under Device Name
        for i in range(total_bags):
            if i == 0:
                time_diff = 120
            else:
                time_diff = (milldata_today[i].katta_time - milldata_today[i - 1].katta_time).total_seconds()
            if time_diff > 300:
                adjusted_time_diff = time_diff - 120
                machine_off_time.append(adjusted_time_diff)
                machine_on_time.append(120)
            else:
                machine_on_time.append(time_diff)

        #To calculate Average Time to show at top
        avg_time = (sum(machine_on_time) / total_bags)/2 if total_bags >= 1 else 0
        avg_per_hour = 3600 / avg_time if avg_time > 0 else 0

        # Calculate averages
        avg_L5 = 3600/(sum(L5) / len(L5)) if L5 else 0
        avg_L10 = 3600/(sum(L10) / len(L10)) if L10 else 0
        avg_L15 = 3600/(sum(L15) / len(L15)) if L15 else 0
        avg_L20 = 3600/(sum(L20) / len(L20)) if L20 else 0

        # Calculation ofr predicted bags
        remaining_hours = 24 - today.hour
        predicted_bags_remaining = remaining_hours * avg_per_hour
        predicted_bags_today = total_bags + predicted_bags_remaining

        # Reverse order of milldata_today and get the last 30 records
        milldata_today = milldata_today.order_by('-katta_time')

        # Pagination
        paginator = Paginator(milldata_with_avg, 30)  # Display 30 records per page
        page = self.request.GET.get('page')
        milldata_paged = paginator.get_page(page)

        context['total_bags'] = total_bags
        context['average_time'] = avg_time
        context['average_per_hour'] = avg_per_hour
        context['predicted_bags_today'] = int(predicted_bags_today)
        #new context
        context['start_date'] = start_date
        context['end_date'] = end_date
        context['milldata_paged'] = milldata_paged
        # context['milldata_today'] = milldata_today[0]
        if milldata_today:      
            context['milldata_today'] = milldata_today[0]        
        else:
            context['milldata_today'] = [0]        
        context['avg_L5'] = avg_L5
        context['avg_L10'] = avg_L10
        context['avg_L15'] = avg_L15
        context['avg_L20'] = avg_L20

        return context


def get_device_data(request, device):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if start_date_str and end_date_str:
        start_date_naive = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date_naive = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1, seconds=-1)

        # Make the start and end dates timezone-aware
        local_tz = pytz.timezone('Asia/Kolkata')
        start_date = local_tz.localize(start_date_naive)
        end_date = local_tz.localize(end_date_naive)
    else:
        today = timezone.now()
        start_date = end_date = today

    milldata_list = Milldata.objects.filter(device=device, katta_time__date__range=(start_date, end_date)).order_by('katta_time')
    total_bags = len(milldata_list)
    if total_bags:
        if total_bags==1:
            average_time = 120
        else:
            average_time = (milldata_list[total_bags-1].katta_time - milldata_list[0].katta_time).total_seconds() / (total_bags)
    else:
        average_time = 0

    return start_date, end_date, milldata_list, total_bags, average_time


def export_pdf(request, device_id):
    device = Device.objects.get(pk=device_id)
    start_date, end_date, milldata_list, total_bags, average_time = get_device_data(request, device)
    average_time = round(average_time, 2)

    # Create the PDF file
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=portrait(letter))

    # Prepare the data for the table
    data = [['Bag Number', 'Fill Time', 'Bag Day-Time', 'Avg Per Hour']]
    for index, milldata in enumerate(milldata_list):
        if index > 0:
            fill_time = round((milldata.katta_time - milldata_list[index - 1].katta_time).total_seconds(), 2)
            if fill_time > 0:
                avg_per_hour = round((3600 / fill_time), 2)
            else:
                avg_per_hour = 0
        else:
            fill_time = 0
            avg_per_hour = 0
        data.append([index + 1, fill_time, milldata.katta_time, avg_per_hour])

    # Create the table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    # Add the table to the PDF document
    doc.build([table])

    # Return the PDF as a response
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='milldata.pdf')

def export_excel(request, device_id):
    device = Device.objects.get(pk=device_id)
    start_date, end_date, milldata_list, total_bags, average_time = get_device_data(request, device)

    # Create the Excel file
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Milldata')

    # Prepare the header row
    header_format = workbook.add_format({'bold': True, 'bg_color': 'gray', 'font_color': 'white'})
    worksheet.write(0, 0, 'Bag Number', header_format)
    worksheet.write(0, 1, 'Fill Time', header_format)
    worksheet.write(0, 2, 'Bag Day-Time', header_format)
    worksheet.write(0, 3, 'Avg Per Hour', header_format)

    # Write the data rows
    for index, milldata in enumerate(milldata_list):
        if index > 0:
            fill_time = round((milldata.katta_time - milldata_list[index - 1].katta_time).total_seconds(), 2)
            if fill_time > 0:
                avg_per_hour = round((3600 / fill_time), 2)
            else:
                avg_per_hour = 0
        else:
            fill_time = 0
            avg_per_hour = 0
        worksheet.write(index + 1, 0, index + 1)
        worksheet.write(index + 1, 1, fill_time)
        worksheet.write(index + 1, 2, milldata.katta_time.strftime('%Y-%m-%d %H:%M:%S'))
        worksheet.write(index + 1, 3, avg_per_hour)

    # Set the column widths
    worksheet.set_column(0, 0, 15)
    worksheet.set_column(1, 1, 15)
    worksheet.set_column(2, 2, 20)
    worksheet.set_column(3, 3, 15)

    # Close the workbook and return the Excel file as a response
    workbook.close()
    output.seek(0)
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=milldata.xlsx'
    return response


class DeviceDataAPI(View):
    def get(self, request, *args, **kwargs):
        device_id = kwargs['device_id']
        try:
            device = Device.objects.get(id=device_id)
        except Device.DoesNotExist:
            return JsonResponse({'error': 'Device not found'}, status=404)

        data = {
            'name': device.name,
            'ip_address': device.ip_address,
            'mac_address': device.mac_address,
            'status': device.status,
            'wait_bags': device.wait_bags,
            'initial_hold': device.initial_hold,
            'circle': device.circle,
            'feed_time': device.feed_time,
            'circle_hold': device.circle_hold,
            'galla_clear_time': device.galla_clear_time,
            'actual_hold': device.actual_hold,
            'overload_hold': device.overload_hold,
            'galla_vibrator_status': device.galla_vibrator_status,
            'hopper_vibrator_status': device.hopper_vibrator_status,
            'extra_time_hold': device.extra_time_hold,
        }
        # Reset extra_time_hold value to 0
        device.extra_time_hold = 0
        device.save()

        return JsonResponse(data)

class CompanyListCreateAPIView(generics.ListCreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsSuperUserOrStaff]

class DeviceListCreateAPIView(generics.ListCreateAPIView):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [IsSuperUserOrStaff]
