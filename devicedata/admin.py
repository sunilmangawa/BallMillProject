from django.contrib import admin
from .models import Company, Device, Milldata

# Register your models here.
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'address', 'city', 'state', 'country', 'owner', 'contract_start_date', 'contract_end_date')
    list_filter = ('name', 'city', 'state', 'owner')
    search_fields = ('name', 'email', 'address', 'city', 'state', 'country', 'owner__username')
    
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'device_id', 'status')
    list_filter = ('status', 'company')
    search_fields = ('name', 'device_id', 'ip_address', 'mac_address')
class MilldataAdmin(admin.ModelAdmin):
    list_display = ['device', 'katta_time', 'katta_weight', 'circle', 'feed_time', 'circle_hold', 'actual_hold', 'feed_status', 'overload_status']
    list_filter = ['device', 'feed_status', 'overload_status']
    search_fields = ['device__name']


admin.site.register(Company, CompanyAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(Milldata, MilldataAdmin)
