# milldata/models.py
from django.db import models
from django.contrib.auth import get_user_model
class Company(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=10)
    state = models.CharField(max_length=15)
    country = models.CharField(max_length=10)
    postal_code = models.IntegerField()
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    contract_start_date = models.DateField(null=True, blank=True)
    contract_end_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return self.name

class Device(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=255)
    ip_address = models.CharField(max_length=15, null=True, blank=True)
    mac_address = models.CharField(max_length=17, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    wait_bags =models.IntegerField(default=3, null=False, blank=True)
    initial_hold = models.IntegerField(default=600)
    circle = models.IntegerField(default=21)
    feed_time = models.IntegerField(default=6)
    circle_hold = models.IntegerField(default=15)
    galla_clear_time = models.IntegerField(default=20)
    actual_hold = models.IntegerField(default=900)
    overload_hold = models.IntegerField(default=2100)
    galla_vibrator_status = models.BooleanField(default=True)
    hopper_vibrator_status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Milldata(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    katta_time = models.DateTimeField( )
    katta_weight = models.FloatField(null=True, blank=True)
    initial_hold = models.IntegerField()
    circle = models.IntegerField() # circle mean loop
    feed_time = models.IntegerField()
    circle_hold = models.IntegerField()
    galla_clear_time = models.IntegerField()
    actual_hold = models.IntegerField()
    overload_hold = models.IntegerField()
    feed_status = models.BooleanField(default=True)
    overload_status = models.BooleanField(default=False)
    

    def __str__(self):
        return f"{self.device.name}"