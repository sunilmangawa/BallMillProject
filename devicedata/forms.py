from django import forms
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from devicedata.models import Device


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')


class EditFeedingForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['wait_bags', 'initial_hold', 'circle', 'feed_time', 'circle_hold', 'galla_clear_time', 'actual_hold', 'overload_hold', 'galla_vibrator_status', 'hopper_vibrator_status','extra_time_hold']
        labels = {
            'wait_bags' : 'Wait of Bags',
            'initial_hold': 'Initial hold',
            'circle': 'Circle',
            'feed_time': 'Feed Time',
            'circle_hold': 'Circle Hold',
            'galla_clear_time': 'Galla Clear Time',
            'actual_hold': 'Actual Hold',
            'overload_hold': 'Overload Hold',
            'galla_vibrator_status': 'Galla Vibrator Status',
            'hopper_vibrator_status': 'Hopper Vibrator Status',
            'extra_time_hold': 'Extra Hold Time'
        }
