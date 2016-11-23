from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import *
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
    folders = models.Folder.objects.filter(owned_by=request.user)
    
    if request.method == 'POST':
        folder_form = FolderForm(request.POST)

        if folder_form.is_valid():
            folder = models.Folder.objects.create(
                name=request.POST.get('name'),
                owned_by=request.user,
                created=datetime.datetime.now()
                )
            folder.save()
    else:
        folder_form = FolderForm()

    return render(request, 'fileshare/main.html',
        {'your_reports': your_reports, 'num_reports': num_reports, 'other_reports': other_reports, 'folder_form':folder_form, 'folders':folders})

@login_required(login_url='login')
def create_report(request):
    
    if request.method == 'POST':
        report_form = ReportForm(request.POST, request.FILES)

        if report_form.is_valid():
            newdoc = models.Report.objects.create(
                owned_by = request.user,
                created = datetime.datetime.now(),
                last_modified = datetime.datetime.now(),
                last_modified_by = request.user.username,
                short_desc = report_form.cleaned_data['short_desc'],
                long_desc = report_form.cleaned_data['long_desc'],
                private = report_form.cleaned_data['private']
            )
            newdoc.save()
            for f in request.FILES.getlist('files'):
                d = models.Documents.objects.create(file_attached=f)
                newdoc.files.add(d)
            newdoc.save()

            return redirect('main')
    
    else:
        report_form = ReportForm()

    return render(request, 'fileshare/create_report.html', {'report_form': report_form})

@login_required(login_url='login')
def view_report(request, report_id):

    report = get_object_or_404(models.Report, pk=report_id)
    files = report.files

    if report.private and request.user != report.owned_by:
        return redirect('main')

    elif request.method == "POST":
        update_form = ReportForm(request.POST, request.FILES, instance=report)

        if update_form.is_valid():
            
            if request.POST.get('action') == "Save Changes":
                report.last_modified = datetime.datetime.now()
                report.last_modified_by = request.user.username
                for f in request.FILES.getlist('files'):
                    d = models.Documents.objects.create(file_attached=f)
                    report.files.add(d)
                report.save()
                update_form.save()
                return redirect('main')
            else:
                report.delete()
                return redirect('main')
    else:
        update_form = ReportForm(instance=report)


    return render(request, 'fileshare/view_report.html', {'report': report, 'update_form': update_form, 'files': files})

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

@login_required(login_url='login')
def create_group(request):
    if request.method == 'POST':
        group_form = GroupForm(request.POST)
        if group_form.is_valid():

            group_form.save()
            instance = models.ProfileGroup.objects.get(name=request.POST.get('name'))

            members_added = request.POST.getlist('members')
            for m in members_added:
                get_object_or_404(models.Profile, pk=m).groups_in.add(instance)

            instance.creator = request.user
            instance.save()

            return redirect('main') #group made successfully
    else:
        #group_form=GroupForm()
        members = models.Profile.objects.all()

    return render(request, 'fileshare/create_group.html', {'members': members})

@login_required(login_url='login')
def view_group(request, group_id):

    group = get_object_or_404(models.ProfileGroup, pk=group_id)

    if request.user.profile not in group.members.all():
        return redirect('main')
    elif request.method == "POST":
        update_form = GroupForm(request.POST, instance=group)

        if update_form.is_valid():

            if request.POST.get('action') == "Save Changes":
                update_form.save()
                return redirect('main')
            else:
                group.delete()
                return redirect('main')
    else:
        update_form = GroupForm(instance=group)

    return render(request, 'fileshare/view_group.html', {'group': group, 'update_form': update_form})

@login_required(login_url='login')
def view_folder(request, folder_id):

    folder = get_object_or_404(models.Folder, pk=folder_id)
    all_reports = models.Report.objects.filter(owned_by=request.user)
    able_to_add = all_reports.exclude(id__in=folder.reports.all())

    if folder.owned_by != request.user:
        return redirect('main')
    elif request.method == "POST":
        update_form = FolderForm(request.POST, instance=folder)

        action = request.POST.get('action')
        if action != "view" and action != "Update" and action != "Delete":
            report = get_object_or_404(models.Report, pk=action)
            folder.reports.add(report)
            folder.save()
            return redirect('main') 

        elif update_form.is_valid():
            if action == "Update":
                update_form.save()
                return redirect('main')
            else:
                folder.delete()
                return redirect('main')

    else:
        update_form = FolderForm(instance=folder)

    return render(request, 'fileshare/view_folder.html', 
        {'folder':folder, 'update_form': update_form, 'all_reports': all_reports, 'able_to_add': able_to_add})







    '''report = get_object_or_404(models.Report, pk=report_id)

    if request.method == "POST":
        update_form = ReportForm(request.POST, request.FILES, instance=report)

        if update_form.is_valid():
            
            if request.POST.get('action') == "Save Changes":
                report.last_modified = datetime.datetime.now()
                report_form.last_modified_by = request.user.username
                update_form.save()
                return redirect('main')
            else:
                report.delete()
                return redirect('main')
    else:
        update_form = ReportForm(instance=report)

    return render(request, 'fileshare/view_report.html', {'report': report, 'update_form': update_form})'''

#site manager views
def sitemanager(request):
    if (request.user.is_staff):
        return render(request,'fileshare/sitemanager.html')

def manage_users(request):
    if (request.user.is_staff):
        all_users = models.User.objects.all()
        return render(request,'fileshare/manage_users.html',{'all_users':all_users})

def manage_reports(request):
    if (request.user.is_staff):
        all_reports = models.Report.objects.all()
        return render(request,'fileshare/manage_reports.html',{'all_reports':all_reports})

def manage_groups(request):
    if(request.user.is_staff):
        all_groups = models.ProfileGroup.objects.all()
        return render(request, 'fileshare/manage_groups.html',{'all_groups':all_groups})

def edit_user(request):
    all_users = models.User.objects.all()
    #return redirect(manage_users)
    return render(request, 'fileshare/edit_user.html')

def edit_group(request):
    all_groups = models.ProfileGroup.objects.all()
    return render(request, 'fileshare/edit_group.html')
#def update_user_permissions(request):
