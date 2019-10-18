import datetime

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template import RequestContext
from django.urls import reverse, reverse_lazy

from users.models import Profile

from .datecounter import dateDiffInSeconds, daysHoursMinutesSecondsFromSeconds,total_days
from .email import *
from .forms import AddEmployeeForm, LeaveForm
from .models import Leave, LeaveType

# Create your views here.

def homepage(request):
    todays_date = datetime.datetime.now()

    return render(request, 'sanergytemplates/homepage.html',{'todays_date':todays_date})


@login_required
def addEmployee(request):
    current_user = request.user
    if request.method == 'POST':
        form = AddEmployeeForm(request.POST)
        if form.is_valid():
            
            name=form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1') 
            form.save()
            welcome_email(name,email, password)

            employee=Profile.objects.filter(user__username=name).first()

            employee.department=current_user.profile.department

            employee.save()

            messages.success(request,'Employee added succesfully')
            return redirect('managersite')

    else:

        form=AddEmployeeForm()

    return render(request, 'admins/add_employee.html', {'form': form})



@login_required(login_url="/login/")
def employee_list(request):
    all_users = User.objects.all()
    return render (request, 'admins/employee_list.html', {'all_users':all_users})


@login_required
def apply_leave(request):

    current_user = request.user

    if current_user.is_superuser == True:
        return redirect(hrsite)

        # return render(request, 'admins/hr.html')
    elif current_user.is_staff==True:
        return redirect(departmental_leaves)

    else:

        requested_days = 0
        if request.method == 'POST':
            form = LeaveForm(request.POST, request.FILES)
            if form.is_valid():
                leave = form.save(commit=False)
                leave.user = current_user

                start_date = form.cleaned_data['Begin_Date']
                end_date = form.cleaned_data['End_Date']



                # <class 'sanergy_leave.models.LeaveType'>
                # leave_type = form.cleaned_data['Leave_Type']
                # print(type(leave_type.Leave_Types),'tpreeeeeeeeeeeeeeeee')
                # leave_name = LeaveType.objects.filter(Leave_Types=leave_type.Leave_Types).first()
                # current_user_leaves=Leave.objects.filter(user=current_user).filter(Leave_Type__Leave_Types=leave_name.Leave_Types)
                # days=[]


                requested_days = daysHoursMinutesSecondsFromSeconds(dateDiffInSeconds(start_date, end_date))



                # for leave in current_user_leaves:
                #     days.append(leave.Requested_Days)

                # total=sum(days)+int(requested_days)
                # print(type(leave_name),current_user_leaves,days,total,requested_days,'totaaaaaaaaaaaaaaaaaaaaaal') 

                # if total>leave_name.leave_limit:
                #     messages.warning(request,f'You have exceed your {leave_name.Leave_Types} limit')
                #     return redirect('apply_leave')



                leave.Requested_Days = requested_days

                name = current_user.username
                superusers = User.objects.filter(is_superuser=True)
                managers = User.objects.filter(is_staff=True).filter(is_superuser=False)
                print(managers, 'manageeeeeeeeeeeeeeeeeeeeeeeeeeers')


                for user in superusers:
                    leave_request_sent(name,user.email)
                for user in managers:
                    if user.profile.department.department_name == current_user.profile.department.department_name:
                        name = user.username
                        leave_request_sent(name,user.email)


                leave.save()

                return redirect('table')    
            

        else:
            form = LeaveForm()
            current_user = request.user
            department_leaves = Leave.objects.filter(user__profile__department__department_name = current_user.profile.department.department_name).all()
            
    return render(request, 'sanergytemplates/leave_apply.html', {"lform": form, 'requested_days': requested_days, 'department_leaves':department_leaves})


def table (request):
    current_user = request.user
    leaves = Leave.objects.filter(user = current_user).order_by('-applying_date')
    return render(request, 'sanergytemplates/table.html',{ "leavess": leaves})


@staff_member_required
def hrsite(request):
    employees=Profile.objects.filter(is_employee=True).all().order_by('joined_date')
    leaves = Leave.print_all().order_by('applying_date')
    return render(request, 'admins/hr.html',{'employees':employees , "leavess": leaves})


@login_required
def accept_leave(request,pk):
 
    leave=Leave.objects.get(pk=pk)
    leave.leave_status=Leave.Approved

    name=leave.user.username
    email =leave.user.email
    date = leave.Begin_Date
    date2 = leave.End_Date
    leave.save()
    status_approval_email(name,email,date,date2)
    messages.success(request,'Leave Approval notification sent')
    return redirect('managersite')


@login_required
def decline_leave(request,pk):
    leave=Leave.objects.get(pk=pk)
    leave.leave_status=Leave.Declined

    name=leave.user.username
    email =leave.user.email
    leave.save()

    status_declined_email(name,email)
    messages.success(request,'Leave Decline notification sent')
    return redirect('managersite')


# vew for manager to get leave requests of his department employees 
@login_required
def managersite(request):
    current_user = request.user

    department_employees = Profile.objects.filter(department = current_user.profile.department).all().order_by('joined_date')
    # department leaves query 
    return render (request, 'admins/manager.html', {'department_employees':department_employees})

@login_required
def departmental_leaves(request):
    current_user = request.user

    departmental_leaves = Leave.objects.filter(user__profile__department__department_name=current_user.profile.department.department_name).all().order_by('-applying_date')

    return render (request, 'sanergytemplates/department_employeesonleave.html', {'departmental_leaves':departmental_leaves})

