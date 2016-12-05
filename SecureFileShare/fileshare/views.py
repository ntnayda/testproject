from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from Crypto.Util import asn1
from base64 import b64decode
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
from django.contrib.auth import models as authmodels
from django.core.files.storage import FileSystemStorage
import datetime
from django import forms as djangoforms
from django.core.urlresolvers import reverse
from Crypto.PublicKey import RSA
from Crypto import Random
import base64
import os
import binascii
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import json



# Create your views here.
def ByteToHex(byteStr):
    """
    Convert a byte string to it's hex string representation e.g. for output.
    """

    # Uses list comprehension which is a fractionally faster implementation than
    # the alternative, more readable, implementation below
    #
    #    hex = []
    #    for aChar in byteStr:
    #        hex.append( "%02X " % ord( aChar ) )
    #
    #    return ''.join( hex ).strip()

    return ''.join(["%02X " % ord(x) for x in byteStr]).strip()


def HexToByte(hexStr):
    """
    Convert a string hex byte values into a byte string. The Hex Byte values may
    or may not be space separated.
    """
    # The list comprehension implementation is fractionally slower in this case
    #
    #    hexStr = ''.join( hexStr.split(" ") )
    #    return ''.join( ["%c" % chr( int ( hexStr[i:i+2],16 ) ) \
    #                                   for i in range(0, len( hexStr ), 2) ] )

    bytes = []

    hexStr = ''.join(hexStr.split(" "))

    for i in range(0, len(hexStr), 2):
        bytes.append(chr(int(hexStr[i:i + 2], 16)))

    return ''.join(bytes)

@csrf_exempt
def fda_login(request,username,password):
    print("username: " + username)
#     print("password: " + password)
    user = authenticate(username = username, password = password)
    if user is not None:
        login(request, user)
        your_reports = models.Report.objects.filter(owned_by=user)
        other_reports = models.Report.objects.filter(private=False).exclude(owned_by=user)
        viewable_reports = []
        for your_report in your_reports:
            num_attachments = len(your_report.files.all())
            report_data = {"report_id":your_report.id, "title":your_report.short_desc, "attachments":num_attachments}
            viewable_reports.append(report_data)
        for other_report in other_reports:
            num_attachments = len(other_report.files.all())
            report_data = {"report_id":other_report.id, "title":other_report.short_desc, "attachments":num_attachments}
            viewable_reports.append(report_data)
        
        return HttpResponse(json.dumps(viewable_reports))
        
    return HttpResponse('Login Failed!')

@csrf_exempt
def fda_report_files(request,report_id):
    user = request.user
    if user is not None:
        report = models.Report.objects.filter(pk=report_id)[0]
        downloadable_files = []
        for file in report.files.all():
            filedata = {"id":file.id, "file_name":file.file_attached.name, "is_encrypted":file.is_encrypted, "file_hash":file.file_hash}
            downloadable_files.append(filedata)
        
        return HttpResponse(json.dumps(downloadable_files))
    
    return HttpResponse('Login Failed!')

def register_success(request):
    return render(request, 'fileshare/register_success.html')

@login_required(login_url='login')
def main(request):
    your_reports = models.Report.objects.filter(owned_by=request.user)
    num_reports = len(your_reports)
    other_reports = models.Report.objects.filter(private=False).exclude(owned_by=request.user)
    folders = models.Folder.objects.filter(owned_by=request.user)
    activity = models.Activity.objects.filter(owned_by=request.user).order_by('time').reverse()
    if request.method == 'POST':
        folder_form = FolderForm(request.POST)
        search_form = SearchForm(request.POST)

        if search_form.is_valid():
            cd = search_form.cleaned_data
            #request.session['param'] = cd.get('param')
            #request.session['query'] = cd.get('query')
            #return redirect('search_results')

        elif folder_form.is_valid():
            folder = models.Folder.objects.create(
                name=request.POST.get('name'),
                owned_by=request.user,
                created=datetime.datetime.now()
            )
            folder.save()
            newactivity = models.Activity.objects.create(owned_by=request.user, time=datetime.datetime.now(),
                                                         description="Created " + str(folder.name))
            newactivity.save()
    else:
        folder_form = FolderForm()
        search_form = SearchForm()

    return render(request, 'fileshare/main.html',
                  {'your_reports': your_reports, 'num_reports': num_reports, 'other_reports': other_reports,
                   'folder_form': folder_form, 'folders': folders, 'search_form': search_form,'activity':activity})


@login_required(login_url='login')
def create_report(request):
    if request.method == 'POST':
        report_form = ReportForm(request.POST, request.FILES)

        if report_form.is_valid():
            newdoc = models.Report.objects.create(
                owned_by=request.user,
                created=datetime.datetime.now(),
                last_modified=datetime.datetime.now(),
                last_modified_by=request.user.username,
                short_desc=report_form.cleaned_data['short_desc'],
                long_desc=report_form.cleaned_data['long_desc'],
                private=report_form.cleaned_data['private'],
                is_encrypted=report_form.cleaned_data['is_encrypted']
            )
#             newdoc.save()
            json_data = request.POST.get('file_hash')
            if json_data != "":
                file_hashes = json.loads(json_data)
            print("file_hash: " + json_data)
            for f in request.FILES.getlist('files'):
                fHash = getFileHashFromData(file_hashes, f.name)
                d = models.Documents.objects.create(file_attached=f, is_encrypted=report_form.cleaned_data['is_encrypted'], file_hash=fHash)
                newdoc.files.add(d)
            newdoc.save()
            newactivity = models.Activity.objects.create(owned_by=request.user,time=datetime.datetime.now(),description="Created " + newdoc.short_desc)
            newactivity.save()

            return redirect('main')

    else:
        report_form = ReportForm()

    return render(request, 'fileshare/create_report.html', {'report_form': report_form})


@login_required(login_url='login')
def view_report(request, report_id):
    report = get_object_or_404(models.Report, pk=report_id)
    files = report.files
    encrypted = report.is_encrypted
    report_comments = report.comments

    # if(request.user.is_staff == False):
    if report.private and request.user != report.owned_by and request.user.is_staff is False:
        return redirect('main')

    elif request.method == "POST":
        print("here1")
        update_form = ReportForm(request.POST, request.FILES, instance=report)
        comment_form = ReportCommentsForm(request.POST)

        if request.POST.get('action')[0] == "f":
            print("here2")
            report.last_modified = datetime.datetime.now()
            report.last_modified_by = request.user.username
            d = get_object_or_404(models.Documents, pk=request.POST.get('action')[1:])
            # remove document from the file system
            fs = FileSystemStorage()
            fs.delete(d.file_attached)
            # remove document from database
            d.delete()
            report.save()
            newactivity = models.Activity.objects.create(owned_by=request.user, time=datetime.datetime.now(),
                                                         description="Modified " +
                                                                     str(report.short_desc))
            newactivity.save()

        elif comment_form.is_valid():
            c = models.ReportComments.objects.create(
                creator = request.user.profile,
                timestamp = datetime.datetime.now(),
                comment = request.POST.get('comment')
                )
            report.comments.add(c)
            report.save()
            c.save()
            newactivity = models.Activity.objects.create(owned_by=request.user, time=datetime.datetime.now(),
                                                         description="You commented on " +
                                                                     str(report.short_desc))
            newactivity.save()
            if (report.owned_by != request.user):
                newactivity = models.Activity.objects.create(owned_by=report.owned_by, time=datetime.datetime.now(),
                                                         description= str(request.user.username) + " commented on " +
                                                                     str(report.short_desc))
                newactivity.save()

        elif update_form.is_valid():
            print("here3")
            if request.POST.get('action') == "Save Changes":
                print("here4")
                report.last_modified = datetime.datetime.now()
                report.last_modified_by = request.user.username
                is_encrypted = not request.POST.get('is_encrypted', None) == None
                json_data = request.POST.get('file_hash')
                if json_data != "":
                    file_hashes = json.loads(json_data)
                print("file_hash: " + json_data)
                for f in request.FILES.getlist('files'):
                    fHash = getFileHashFromData(file_hashes, f.name)
                    d = models.Documents.objects.create(file_attached=f, is_encrypted=is_encrypted, file_hash=fHash)
                    report.files.add(d)
                report.save()
                update_form.save()
                newactivity = models.Activity.objects.create(owned_by=request.user, time=datetime.datetime.now(),
                                                             description="Modified " +
                                                                         str(report.short_desc))
                newactivity.save()
                return redirect('main')
            
            if request.POST.get('action')[0] == "f":
                print("here5")
                report.last_modified = datetime.datetime.now()
                report.last_modified_by = request.user.username
                d = get_object_or_404(models.Documents, pk=request.POST.get('action')[1:])
                d.delete()
                newactivity = models.Activity.objects.create(owned_by=request.user, time=datetime.datetime.now(),
                                                             description="Modified " +
                                                                         str(report.short_desc))
                newactivity.save()
                return redirect('main')

            else:
                print("here6")
                report.delete()
                return redirect('main')
    else:
        update_form = ReportForm(instance=report)
        comment_form = ReportCommentsForm()

    return render(request, 'fileshare/view_report.html', {'report': report, 'update_form': update_form, 'files': files, 'num_files': files.count(), 'encrypted': encrypted, 'comment_form': comment_form, 'report_comments': report_comments})

def getFileHashFromData(data, filename):
    for file in data:
        if file["filename"] == filename:
            return file["file_hash"]



@login_required(login_url='login')
def view_group_report(request, report_id, profilegroup_id):
    report = get_object_or_404(models.Report, pk=report_id)
    group = get_object_or_404(models.ProfileGroup, pk=profilegroup_id)
    files = report.files
    encrypted = report.is_encrypted

    if request.user.profile not in group.members.all():
        return redirect('main')

    return render(request, 'fileshare/view_group_report.html', {'report': report, 'group': group, 'encrypted': encrypted, 'files': files, 'num_files': files.count()})

@login_required(login_url='login')
def user_delete_report(request, report_id):
    report = get_object_or_404(models.Report, pk=report_id)
    newactivity = models.Activity.objects.create(owned_by=request.user, time=datetime.datetime.now(),
                                                 description="Deleted " + report.short_desc)
    newactivity.save()
    # remove all file attachments from the file system
    fs = FileSystemStorage()
    files = report.files.all()
    for file in files:
        fs.delete(file.file_attached)
        file.delete()
    # remove report from database
    report.delete()
    return HttpResponseRedirect('/main')



@login_required(login_url='login')
def account_update_success(request):
    return render(request, 'fileshare/account_update_success.html')


@login_required(login_url='login')
def account(request):
    return render(request, 'fileshare/account.html')

@login_required(login_url='login')
def messages(request):
    user = request.user
    user.profile.unreadmessages = "false"
    user.profile.save()
    form = forms.messageForm(request.POST or None)
    if request.method == 'POST':
        if (request.POST['newmessagefield'] == "Yes"):
            # sender data

            newconvo = models.Conversation.objects.create(sender=user,
                                                          reciever=models.User.objects.get(id=request.POST['sender']),
                                                          reciever_name=user.username + "-" + models.User.objects.get(
                                                              id=request.POST[
                                                                  'sender']).username,
                                                          recently_used=datetime.datetime.now(),unreadmessages="0"
                                                          )
            newconvo.save()
            if(request.POST['thekey']!="True"):
                newmessage = models.Message.objects.create(owned_by=newconvo,
                                                           sender=user,
                                                           messagecontent=request.POST['messagecontent'],
                                                           time=datetime.datetime.now(), key=request.POST['thekey'])
                newmessage.save()




            # reciever data
            newconvo2 = models.Conversation.objects.create(reciever=user,
                                                           sender=models.User.objects.get(id=request.POST['sender']),
                                                           reciever_name=models.User.objects.get(
                                                               id=request.POST[
                                                                   'sender']).username + "-" + user.username,
                                                           recently_used=datetime.datetime.now(),unreadmessages="1"
                                                           )
            newconvo2.save()
            otheruser = newconvo2.sender
            print(otheruser.username)
            print(otheruser.profile.unreadmessages)
            otheruser.profile.unreadmessages = "true"
            otheruser.profile.save()
            print(otheruser.profile.unreadmessages)

            if (request.POST['thekey'] == "True"):
                thekey = RSA.importKey(newconvo2.sender.profile.publickey)
                messagetoencrypt = str(request.POST['messagecontent'])
                encryptedmessage = thekey.encrypt(messagetoencrypt.encode(), 1)
                encryptedmessage = encryptedmessage[0];
                encryptedmessage = base64.b16encode(encryptedmessage)
                encryptedmessage = str(encryptedmessage, 'ascii')
                newmessage2 = models.Message.objects.create(owned_by=newconvo2,
                                                           sender=user,
                                                           messagecontent=encryptedmessage,
                                                           time=datetime.datetime.now(), key=request.POST['thekey'])
                newmessage2.save()

            else:
                newmessage2 = models.Message.objects.create(owned_by=newconvo2,
                                                           sender=user,
                                                           messagecontent=str(request.POST['messagecontent']),
                                                           time=datetime.datetime.now(), key=request.POST['thekey'])
                newmessage2.save()


            return redirect("/messages")

        elif form.is_valid():

            # sender data
            if (request.POST['thekey'] != "True"):
                newmessage = models.Message.objects.create(owned_by=form.cleaned_data['owned_by'],
                                                           sender=user,
                                                           messagecontent=str(request.POST['messagecontent']),
                                                           time=datetime.datetime.now(), key=request.POST['thekey'])
                newmessage.save()
                convo = form.cleaned_data['owned_by']
                convo.recently_used = newmessage.time
                convo.save()
            convo = form.cleaned_data['owned_by']
            # reciever data

            convo2 = models.Conversation.objects.get(reciever=convo.sender, sender=convo.reciever)
            if (request.POST['thekey'] == "True"):
                thekey = RSA.importKey(convo2.sender.profile.publickey)

                messagetoencrypt = str(request.POST['messagecontent'])
                encryptedmessage = thekey.encrypt(messagetoencrypt.encode(),1)
                encryptedmessage = encryptedmessage[0];
                encryptedmessage = base64.b16encode(encryptedmessage)
                encryptedmessage = str(encryptedmessage,'ascii')
                newmessage2 = models.Message.objects.create(owned_by=convo2,
                                                        sender=user,
                                                        messagecontent=encryptedmessage,
                                                        time=datetime.datetime.now(), key=request.POST['thekey'])
                newmessage2.save()
            else:
                newmessage2 = models.Message.objects.create(owned_by=convo2,
                                                           sender=user,
                                                           messagecontent=str(request.POST['messagecontent']),
                                                           time=datetime.datetime.now(), key=request.POST['thekey'])
                newmessage2.save()

            convo2.recently_used = newmessage2.time
            currentcount = int(convo2.unreadmessages)
            currentcount += 1
            convo2.unreadmessages = str(currentcount)
            convo2.save()
            otheruser = convo2.sender
            print(otheruser.username)
            print(otheruser.profile.unreadmessages)
            otheruser.profile.unreadmessages = "true"
            otheruser.profile.save()
            print(otheruser.profile.unreadmessages)
            return redirect("/messages")

    conversation_list = models.Conversation.objects.all().filter(sender=user).order_by('recently_used').reverse()
    message_list = []
    for convo in conversation_list:
        message_list.append(models.Message.objects.all().filter(owned_by=convo).order_by('time').reverse)
    reciever_list = models.User.objects.all()
    forms.messageForm.base_fields['owned_by'] = djangoforms.ModelChoiceField(queryset=conversation_list, required=False)
    form = forms.messageForm()
    return render(request, 'fileshare/messages.html',
                  {'reciever_list': reciever_list, 'conversation_list': conversation_list, 'message_list': message_list,
                   'form': form})


@login_required(login_url='login')
def update_profile(request):
    user = request.user
    form = forms.UpdateProfile(request.POST or None,
                               initial={'first_name': user.first_name, 'last_name': user.last_name,
                                        'email': user.email})
    if request.method == 'POST':
        if form.is_valid():
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            user.email = request.POST['email']

            user.save()
            newactivity = models.Activity.objects.create(owned_by=request.user, time=datetime.datetime.now(),
                                                         description="Updated profile.")
            newactivity.save()
            return HttpResponseRedirect('/account/view')

    context = {
        "form": form
    }

    return render(request, "fileshare/account_update.html", context)

@login_required(login_url='login')
def password_change(request):
    form = auth_forms.PasswordChangeForm(user=request.user, data=request.POST)
    if request.method == 'POST':

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            newactivity = models.Activity.objects.create(owned_by=request.user, time=datetime.datetime.now(),
                                                         description="Changed password.")
            newactivity.save()
            return HttpResponseRedirect('/logout')
    context = {
        "form": form
    }
    return render(request, "fileshare/changepassword.html", context)


@login_required(login_url='login')
def deletemessage(request, message_pk):
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

            instance.members.add(request.user.profile)
            request.user.profile.groups_in.add(instance)
            members_added = request.POST.getlist('members')
            for m in members_added:
                m = get_object_or_404(models.Profile, pk=m)
                m.groups_in.add(instance)
                instance.members.add(m)
                newactivity = models.Activity.objects.create(owned_by=m.user, time=datetime.datetime.now(),
                                                             description=str(request.user.username) +" added you to " + str(instance.name))
                newactivity.save()
                m.save()

            instance.creator = request.user
            instance.save()
            request.user.profile.save()
            
            newactivity = models.Activity.objects.create(owned_by=request.user, time=datetime.datetime.now(),
                                                         description="Created " + str(instance.name))
            newactivity.save()
            return redirect('main')  # group made successfully
    else:
        # group_form=GroupForm()
        members = models.Profile.objects.all().exclude(user=request.user)

    return render(request, 'fileshare/create_group.html', {'members': members})


@login_required(login_url='login')
def view_group(request, group_id):
    group = get_object_or_404(models.ProfileGroup, pk=group_id)
    #private_reports = request.user.profile.reports_owned.filter(private=True)
    private_reports = models.Report.objects.filter(owned_by=request.user, private=True).exclude(id__in=group.reports.all())
    all_users = models.User.objects.all()
    group_comments = group.comments

    if request.user.profile not in group.members.all() and not request.user.is_staff:
        return redirect('main')
    elif request.method == "POST":
        update_form = UpdateGroupForm(request.POST, instance=group)
        comment_form = ReportCommentsForm(request.POST)
        
        action = request.POST.get('action')
        if action != "Save Changes":
            if action[0] == 'a':
                report = get_object_or_404(models.Report, pk=action[1:])
                group.reports.add(report)
                group.save()
                newactivity = models.Activity.objects.create(owned_by=request.user, time=datetime.datetime.now(),
                                                             description="Added " +
                                                                         str(report.short_desc) + " to " + str(group.name))
                newactivity.save()
            elif action[0] == 'r':
                report = get_object_or_404(models.Report, pk=action[1:])
                newactivity = models.Activity.objects.create(owned_by=request.user, time=datetime.datetime.now(),
                                                             description="Removed " +
                                                                         str(report.short_desc) + " from " + str(group.name))
                newactivity.save()
                group.reports.remove(report)
                group.save()

            
            elif action[0] == 'p':
                m = get_object_or_404(models.Profile, pk=action[1:])
                m.groups_in.add(group)
                group.members.add(m)
                group.save()
                newactivity = models.Activity.objects.create(owned_by=request.user, time=datetime.datetime.now(),
                                                             description="Added " +
                                                                         str(m.user.username) + " to " + str(group.name))
                newactivity.save()
                newactivity = models.Activity.objects.create(owned_by=m.user, time=datetime.datetime.now(),
                                                             description=str(request.user) + " added you to " + str(
                                                                 group.name))
                newactivity.save()

            elif action == 'l':
                request.user.profile.groups_in.remove(group)
                newactivity = models.Activity.objects.create(owned_by=request.user, time=datetime.datetime.now(),
                                                             description="You left " +
                                                                         str(group.name))
                newactivity.save()
                group.members.remove(request.user.profile)
                group.save()
                return redirect('main')

            elif action == 'e':
                group.delete()
                return redirect('main')

            elif action == 'c':
                c = models.ReportComments.objects.create(
                    creator = request.user.profile,
                    timestamp = datetime.datetime.now(),
                    comment = request.POST.get('comment')
                    )
                group.comments.add(c)
                group.save()
                c.save()

            else:
                m = get_object_or_404(models.Profile, pk=action)
                m.groups_in.remove(group)
                group.members.remove(m)
                group.save()
                newactivity = models.Activity.objects.create(owned_by=request.user, time=datetime.datetime.now(),
                                                             description="Removed " +
                                                                         str(m.user.username) + " from " + str(group.name))
                newactivity.save()
                newactivity = models.Activity.objects.create(owned_by=m.user, time=datetime.datetime.now(),
                                                             description=str(request.user) + " removed you from " + str(
                                                                 group.name))
                newactivity.save()

        elif update_form.is_valid():

            if request.POST.get('action') == "Save Changes":
                newactivity = models.Activity.objects.create(owned_by=request.user, time=datetime.datetime.now(),
                                                             description="Edited " +
                                                                         str(group.name))
                newactivity.save()
                update_form.save()
                
            else:
                newactivity = models.Activity.objects.create(owned_by=request.user, time=datetime.datetime.now(),
                                                             description="Removed yourself from " +
                                                                         str(group.name))
                newactivity.save()
                group.delete()
                return redirect('main')

    else:
        update_form = UpdateGroupForm(instance=group)
        comment_form = ReportCommentsForm()

    return render(request, 'fileshare/view_group.html', {'group': group, 'update_form': update_form, 'private_reports': private_reports, 'all_users': all_users, 'comment_form': comment_form, 'group_comments': group_comments})



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
            report = get_object_or_404(models.Report, pk=action[1:])
            if action[0] == 'a':
                folder.reports.add(report)
                report.in_folder = True
                newactivity = models.Activity.objects.create(owned_by=request.user, time=datetime.datetime.now(),
                                                             description="Added " +
                                                                         str(report.short_desc) + " to " + str(folder.name))
                newactivity.save()
            else:
                folder.reports.remove(report)
                report.in_folder = False
                newactivity = models.Activity.objects.create(owned_by=request.user, time=datetime.datetime.now(),
                                                             description="Removed " +
                                                                         str(report.short_desc) + " from " + str(
                                                                 folder.name))
                newactivity.save()
            folder.save()

        elif update_form.is_valid():
            if action == "Update":
                update_form.save()
                newactivity = models.Activity.objects.create(owned_by=request.user, time=datetime.datetime.now(),
                                                             description="Updated " + str(folder.name))
                newactivity.save()
                return redirect('main')
            else:
                newactivity = models.Activity.objects.create(owned_by=request.user, time=datetime.datetime.now(),
                                                             description="Deleted " +
                                                                         str(folder.name))
                newactivity.save()
                folder.delete()
                return redirect('main')

    else:
        update_form = FolderForm(instance=folder)

    return render(request, 'fileshare/view_folder.html',
                  {'folder': folder, 'update_form': update_form, 'all_reports': all_reports,
                   'able_to_add': able_to_add})


def register(request):
    if request.method == 'POST':
        register_form = signup_form(request.POST)

        if register_form.is_valid():
            newuser = authmodels.User.objects.create(username=request.POST['username'],
                                                     first_name=request.POST['first_name'],
                                                     last_name=request.POST['last_name'],
                                                     email=request.POST['email']
                                                     )
            newuser.set_password(register_form.cleaned_data["password1"])
            newuser.save()

            random_generator = Random.new().read
            key = RSA.generate(1024, random_generator)
            pubkey = key.publickey()
            newuser.profile.publickey = pubkey.exportKey()
            newuser.profile.save()
            newactivity = models.Activity.objects.create(owned_by=newuser, time=datetime.datetime.now(),
                                                         description="Account created.")
            newactivity.save()

            # return HttpResponseRedirect('/register/success/'+str(newuser.id))
            # return(register_success(request,newuser.id))
            return render(request,'fileshare/register_success.html',{'key':str(key.exportKey())})

    else:
        register_form = signup_form()

    return render(request, 'fileshare/register.html', {'form': signup_form()})

# site manager views
@login_required(login_url='login')
def sitemanager(request):
    if (request.user.is_staff):
        return render(request, 'fileshare/sitemanager.html')

@login_required(login_url='login')
def manage_users(request):
    if (request.user.is_staff):
        all_users = models.User.objects.all()
        return render(request, 'fileshare/manage_users.html', {'all_users': all_users})

@login_required(login_url='login')
def manage_reports(request):
    if (request.user.is_staff):
        all_reports = models.Report.objects.all()
        return render(request, 'fileshare/manage_reports.html', {'all_reports': all_reports})

@login_required(login_url='login')
def manage_groups(request):
    if (request.user.is_staff):
        all_groups = models.ProfileGroup.objects.all()
        return render(request, 'fileshare/manage_groups.html', {'all_groups': all_groups})

@login_required(login_url='login')
def edit_user(request, user_id):
    profile = models.Profile.objects.filter(user_id=user_id)
    # print(profile[0].user.username)

    return render(request, 'fileshare/edit_user.html', {'profile': profile[0]})

@login_required(login_url='login')
def sm_update_user(request):
    profile = models.Profile.objects.filter(pk=request.POST['profile_id'])[0]
    user = profile.user

    user.first_name = request.POST['first_name']
    user.last_name = request.POST['last_name']
    user.email = request.POST['email']
    user.is_active = not request.POST.get('is_active', None) == None
    user.is_staff = not request.POST.get('is_staff', None) == None
    user.save()
    newactivity = models.Activity.objects.create(owned_by=request.user, time=datetime.datetime.now(),
                                                 description="Updated " + str(user.username))
    newactivity.save()
    return render(request, 'fileshare/user_update_success.html', {'profile': profile})

@login_required(login_url='login')
def delete_report(request, report_id):
    report = get_object_or_404(models.Report, pk=report_id)
    newactivity = models.Activity.objects.create(owned_by=request.user, time=datetime.datetime.now(),
                                                 description="Deleted " + str(report.short_desc))
    newactivity.save()
    report.delete()
    return HttpResponseRedirect('/manage_reports.html')
    # return render(request, 'fileshare/manage_reports.html')

# return render(request, 'fileshare/sm_update_user.html')
# def edit_group(request):
#     all_groups = models.ProfileGroup.objects.all()
#     return render(request, 'fileshare/edit_group.html')
# def update_user_permissions(request):

def test(request):
    return HttpResponse("test")

@login_required(login_url='login')
def decrypt_message(request, message_pk):
    query = models.Message.objects.get(pk=message_pk)

    if request.method == 'POST':
        decrypt_form = DecryptMessageForm(request.POST)

        password = request.POST['password']
        print(password)
        password = password[2:]
        password = password[:-1]
        password2 = password.replace('\\n','\n')
        password = password[0:24]+password2[24:-25]+password[-25:]
        print(password)
        originalmessage = binascii.unhexlify(query.messagecontent)
        try:
            thekey = RSA.importKey(password)
            pubkey = thekey.publickey()
            encryptedmessage = thekey.decrypt(originalmessage)
        except:
            return render(request,'fileshare/decrypt_message.html', {'message': "Invalid RSA key."})

        return render(request, 'fileshare/decrypt_message.html', {'message': encryptedmessage})
    else:
        decrypt_form = DecryptMessageForm()

    return render(request, 'fileshare/decrypt_message.html', {'form': decrypt_form})

@login_required(login_url='login')
def updateunread(request, message_pk):
    query = models.Conversation.objects.get(pk=message_pk)
    currentcount = query.unreadmessages
    query.unreadmessages = 0
    query.save()
    #usercount = int(request.user.profile.unreadmessages)

    #request.user.profile.save()
    return HttpResponse("success")


@login_required(login_url='login')
def search_results(request):

    query = request.POST.get('search')
    param = request.POST.get('parameter')

    if query is None or query == "":
        return redirect('main')

    usernames = []
    if param == "desc":
        results = models.Report.objects.filter(
            Q(short_desc__icontains=query) | Q(long_desc__icontains=query)
            ).exclude(~Q(owned_by=request.user), Q(private=True))
    elif param == "owner":
        usernames = models.User.objects.filter(username__icontains=query)
        results = models.Report.objects.filter(Q(owned_by__in=usernames)).exclude(~Q(owned_by=request.user ), Q(private=True))
    else: 
        results = []

        # Add support for searching by date created and date modified??

    return render(request, 'fileshare/search_results.html', {'query': query, 'results': results, 'usernames': usernames, 'param': param})
