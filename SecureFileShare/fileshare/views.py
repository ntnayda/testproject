from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import ReportForm
from .forms import GroupForm
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
from django.core.urlresolvers import reverse


# Create your views here.

def register_success(request):
    return render(request,'fileshare/register_success.html')

def profile(request):
	return

@login_required(login_url='login')
def main(request):
	
    your_reports = models.Report.objects.filter(owned_by=request.user)
    num_reports = len(your_reports)

    other_reports = models.Report.objects.filter(private=False).exclude(owned_by=request.user)

    return render(request, 'fileshare/main.html',
        {'your_reports': your_reports, 'num_reports': num_reports, 'other_reports': other_reports})

def create_report(request):
    
    if request.method == 'POST':
        report_form = ReportForm(request.POST, request.FILES)

        if report_form.is_valid():
            #newdoc = models.Report(request.FILES.get('file_attached', False))
            newdoc = models.Report.objects.create(
                owned_by = request.user,
                created = datetime.datetime.now(),
                last_modified = datetime.datetime.now(),
                file_attached = request.FILES.get('file_attached'),
                short_desc = report_form.cleaned_data['short_desc'],
                long_desc = report_form.cleaned_data['long_desc']
            )
            newdoc.save()

            return redirect('main')
    
    else:
        report_form = ReportForm()

    return render(request, 'fileshare/create_report.html', {'report_form': report_form})

def view_report(request, report_id):

    report = get_object_or_404(models.Report, pk=report_id)

    if request.method == "POST":
        update_form = ReportForm(request.POST, request.FILES, instance=report)

        if update_form.is_valid():
            
            if request.POST.get('action') == "Save Changes":
                report.last_modified = datetime.datetime.now()
                update_form.save()
                return redirect('main')
            else:
                report.delete()
                return redirect('main')
    else:
        update_form = ReportForm(instance=report)

    return render(request, 'fileshare/view_report.html', {'report': report, 'update_form': update_form})

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
        if (request.POST['newmessagefield']=="Yes"):
            #sender data
            newconvo = models.Conversation.objects.create(sender=user,
                                                          reciever=models.User.objects.get(id=request.POST['sender']),
                                                          reciever_name=user.username + "-" + models.User.objects.get(id=request.POST[
                                                              'sender']).username,
                                                          recently_used=datetime.datetime.now()
                                                          )
            newconvo.save()
            newmessage = models.Message.objects.create(owned_by=newconvo,
                                                       sender=user,
                                                       messagecontent=request.POST['messagecontent'],
                                                       time=datetime.datetime.now(),key=request.POST['thekey'])
            newmessage.save()


            #reciever data
            newconvo2 = models.Conversation.objects.create(reciever=user,
                                                          sender=models.User.objects.get(id=request.POST['sender']),
                                                          reciever_name= models.User.objects.get(
                                                              id=request.POST[
                                                                  'sender']).username+ "-" +user.username ,
                                                          recently_used=datetime.datetime.now()
                                                          )
            newconvo2.save()
            newmessage2 = models.Message.objects.create(owned_by=newconvo2,
                                                       sender=user,
                                                       messagecontent=request.POST['messagecontent'],
                                                       time=datetime.datetime.now(),key=request.POST['thekey'])
            newmessage2.save()
            return redirect("/messages")

        elif form.is_valid():

            #sender data
            newmessage = models.Message.objects.create(owned_by=form.cleaned_data['owned_by'],
                                                       sender=user,
                                                       messagecontent=request.POST['messagecontent'],
                                                       time=datetime.datetime.now(),key=request.POST['thekey'])
            newmessage.save()
            convo = form.cleaned_data['owned_by']
            convo.recently_used = newmessage.time
            convo.save()

            #reciever data
            convo2 = models.Conversation.objects.get(reciever=convo.sender, sender=convo.reciever)
            newmessage2 = models.Message.objects.create(owned_by=convo2,
                                                       sender=user,
                                                       messagecontent=request.POST['messagecontent'],
                                                       time=datetime.datetime.now(),key=request.POST['thekey'])
            newmessage2.save()

            convo2.recently_used = newmessage.time
            convo2.save()
            return redirect("/messages")





    conversation_list = models.Conversation.objects.all().filter(sender=user).order_by('recently_used').reverse()
    message_list = []
    for convo in conversation_list:
        message_list.append(models.Message.objects.all().filter(owned_by=convo).order_by('time').reverse)

    forms.messageForm.base_fields['owned_by'] = djangoforms.ModelChoiceField(queryset=conversation_list,required=False)
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


def deletemessage(request,message_pk):
    query = models.Message.objects.get(pk=message_pk)
    query.delete()
    return redirect("/messages")

def create_group(request):
    if request.method == 'POST':
        group_form = GroupForm(request.POST)
        if group_form.is_valid():
            group_form.save()
            return redirect('main') #group made successfully
    else:
        #group_form=GroupForm()
        members = models.Profile.objects.all()

    return render(request, 'fileshare/create_group.html', {'members': members})