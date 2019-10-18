from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction

from users.models import Profile

from .models import Leave, Notice


class LeaveForm(forms.ModelForm):

    class Meta:
        model= Leave
        widgets = {
           'Begin_Date':forms.DateTimeInput(attrs={ 'class':
               'datetime-input'}),
            'End_Date':forms.DateTimeInput(attrs={ 'class':
               'datetime-input'}),
        }

        exclude=['empLeave_req_id','emp_id','emp_fullname','user','leave_status','leave_issuer','Requested_Days','leave_balance','applying_date']



class AddEmployeeForm(UserCreationForm):
	email = forms.EmailField()

	class Meta:
		model = User
		fields = ['username','email','password1','password2']



class ManagerSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_manager = True
        if commit:
            user.save()
        return user

class LeaveCommentForm(forms.ModelForm):
    fields = ['Comment']
