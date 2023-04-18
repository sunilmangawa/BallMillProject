from django.urls import path, include
# from django.contrib.auth import views as auth_views
from .views import home_page_view, device_data, CompanyDashboardView, EditFeedingView, MilldataListCreateAPIView, DashboardView, CompanyDetailView, DeviceDetailView, DeviceDataAPI, CompanyListCreateAPIView, DeviceListCreateAPIView  #,  login_view, signup, profile, CompanyListAPIView, DeviceListAPIView, DeviceDetailAPIView,  DeviceDataRangeAPIView
from . import views

urlpatterns = [
    path('dashboard/<int:pk>/', DashboardView.as_view(), name='dashboard'),
    path('company/<int:pk>/', CompanyDetailView.as_view(), name='company_detail'),
    path('device/<int:company_id>/<int:pk>/', DeviceDetailView.as_view(), name='device_detail'),
    path('device/<int:pk>/edit_feeding/', EditFeedingView.as_view(), name='edit_feeding'),
    # API URLS
    path('device/<int:device_id>/data/', device_data, name='device_data'),
    path('companies/', CompanyListCreateAPIView.as_view(), name='company-list-create'),
    path('devices/', DeviceListCreateAPIView.as_view(), name='device-list-create'),
    path('device/<int:device_id>/', DeviceDataAPI.as_view(), name='device-data-api'),
    path('devices/<int:device_id>/timestamps/', MilldataListCreateAPIView.as_view(), name='milldata-list-create'),
    # REPORT URLS
    path('export_pdf/<int:device_id>/', views.export_pdf, name='export_pdf'),
    path('export_excel/<int:device_id>/', views.export_excel, name='export_excel'),
]
