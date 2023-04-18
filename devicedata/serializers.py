from rest_framework import serializers
from .models import Company, Device, Milldata


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class DeviceSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    
    class Meta:
        model = Device
        fields = '__all__'


class MilldataSerializer(serializers.ModelSerializer):
    device = DeviceSerializer(read_only=True)

    class Meta:
        model = Milldata
        fields = '__all__'
        extra_kwargs = {
            'initial_hold': {'required': False},
            'circle': {'required': False},
            'feed_time': {'required': False},
            'circle_hold': {'required': False},
            'galla_clear_time': {'required': False},
            'actual_hold': {'required': False},
            'overload_hold': {'required': False},
        }
