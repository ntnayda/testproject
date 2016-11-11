from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import ReportForm
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect, QueryDict
from . import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import update_session_auth_hash
from . import models
from django.core.files.storage import FileSystemStorage
import datetime
from django import forms as djangoforms

# Create your views here.

def register_success(request):
    return render(request,'fileshare/register_success.html')

def profile(request):
	return

@login_required(login_url='login')
def main(request):
	
    reports = models.Report.objects.filter(owned_by=request.user)
    num_reports = len(reports)

    return render(request, 'fileshare/main.html', {'reports': reports, 'num_reports': num_reports})

def create_report(request):
    
    if request.method == 'POST':
        report_form = ReportForm(request.POST, request.FILES)

        if report_form.is_valid():
            #newdoc = models.Report(request.FILES.get('file_attached', False))
            newdoc = models.Report.objects.create(
                owned_by = request.user,
                created = datetime.datetime.now(),
                file_attached = request.FILES.get('file_attached'),
                short_desc = report_form.cleaned_data['short_desc'],
                long_desc = report_form.cleaned_data['long_desc']
            )
            newdoc.save()

            return redirect('main')
    
    else:
        report_form = ReportForm()

    return render(request, 'fileshare/create_report.html', {'report_form': report_form})

@login_required(login_url='login')
def account_update_success(request):
    return render(request,'fileshare/account_update_success.html')

@login_required(login_url='login')
def account(request):
    return render(request,'fileshare/account.html')

def messages(request):
    user = request.user
    form = forms.messageForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            newmessage = models.Message.objects.create(owned_by=form.cleaned_data['owned_by'],
                                                       sender=user,
                                                       messagecontent=request.POST['messagecontent'],
                                                       time=datetime.datetime.now())
            newmessage.save()
            convo = form.cleaned_data['owned_by']
            convo.recently_used = newmessage.time
            convo.save()
            conversation_list = (models.Conversation.objects.all().filter(
                sender=user) | models.Conversation.objects.all().filter(reciever=user)).order_by('recently_used').reverse()
            message_list = []
            for convo in conversation_list:
                message_list.append(models.Message.objects.all().filter(owned_by=convo))

            return redirect("/messages")
            #return render(request,'fileshare/messages.html',{'conversation_list':conversation_list,'message_list':message_list,'form':forms.messageForm(),'send_pressed':True})


    conversation_list = (models.Conversation.objects.all().filter(sender=user) | models.Conversation.objects.all().filter(reciever=user)).order_by('recently_used').reverse()
    message_list = []
    for convo in conversation_list:
        message_list.append(models.Message.objects.all().filter(owned_by=convo))

    forms.messageForm.base_fields['owned_by'] = djangoforms.ModelChoiceField(queryset=conversation_list)
    form = forms.messageForm()
    return render(request,'fileshare/messages.html',{'conversation_list':conversation_list,'message_list':message_list,'form':form})

def update_profile(request):

    user = request.user
    form = forms.UpdateProfile(request.POST or None, initial={'first_name':user.first_name, 'last_name':user.last_name,'email':user.email})
    if request.method == 'POST':
        if form.is_valid():


            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            user.email = request.POST['email']

            user.save()
            return HttpResponseRedirect('/account/view')

    context = {
        "form": form
    }

    return render(request, "fileshare/account_update.html", context)




def password_change(request):
    form = auth_forms.PasswordChangeForm(user=request.user, data=request.POST)
    if request.method == 'POST':

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return HttpResponseRedirect('/logout')
    context = {
        "form": form
    }
    return render(request,"fileshare/changepassword.html",context)
