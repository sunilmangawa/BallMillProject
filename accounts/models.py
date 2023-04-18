# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
class CustomUser(AbstractUser):
    mobile = models.CharField(max_length=10, null=True, blank=True)
