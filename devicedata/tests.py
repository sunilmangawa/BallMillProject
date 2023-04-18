from django.test import TestCase
from django.urls import reverse
from .models import Company, Device, Milldata
from django.contrib.auth.models import User


class CompanyModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        user = User.objects.create_user(username='testuser', password='testpass')
        Company.objects.create(name='Test Company', email='test@test.com', address='123 Main St', city='Test City',state='Test State', country='Test Country', postal_code=12345, owner=user)

    def test_name_label(self):
        company = Company.objects.get(id=1)
        field_label = company._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_email_max_length(self):
        company = Company.objects.get(id=1)
        max_length = company._meta.get_field('email').max_length
        self.assertEqual(max_length, 254)

    def test_object_name_is_name(self):
        company = Company.objects.get(id=1)
        expected_object_name = f'{company.name}'
        self.assertEqual(expected_object_name, str(company))


class DeviceModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        user = User.objects.create_user(username='testuser', password='testpass')
        company = Company.objects.create(name='Test Company', email='test@test.com', address='123 Main St', city='Test City', state='Test State', country='Test Country', postal_code=12345, owner=user)
        Device.objects.create(name='Test Device', company=company, device_id='ABC123')

    def test_name_label(self):
        device = Device.objects.get(id=1)
        field_label = device._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_device_id_max_length(self):
        device = Device.objects.get(id=1)
        max_length = device._meta.get_field('device_id').max_length
        self.assertEqual(max_length, 255)

    def test_object_name_is_name(self):
        device = Device.objects.get(id=1)
        expected_object_name = f'{device.name}'
        self.assertEqual(expected_object_name, str(device))


class MilldataModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        user = User.objects.create_user(username='testuser', password='testpass')
        company = Company.objects.create(name='Test Company', email='test@test.com', address='123 Main St', city='Test City', state='Test State', country='Test Country', postal_code=12345, owner=user)
        device = Device.objects.create(name='Test Device', company=company, device_id='ABC123')
        Milldata.objects.create(device=device, data={"datetime": '2023-02-27 20:24:53.592027',})

    def test_object_name_is_device_name_data(self):
        milldata = Milldata.objects.get(id=1)
        expected_object_name = f'{milldata.device.name}_data'
        self.assertEqual(expected_object_name, str(milldata))
