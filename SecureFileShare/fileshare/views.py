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
<<<<<<< HEAD
from Crypto.PublicKey import RSA
from Crypto import Random
import base64
import os
import binascii
=======
from django.db.models import Q

>>>>>>> adc7d5419611a530a734e332e028658e3dbcc86e


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

def register_success(request):
    return render(request, 'fileshare/register_success.html')


<<<<<<< HEAD
=======
def profile(request):
    return


>>>>>>> adc7d5419611a530a734e332e028658e3dbcc86e
@login_required(login_url='login')
def main(request):
    your_reports = models.Report.objects.filter(owned_by=request.user)
    num_reports = len(your_reports)
    other_reports = models.Report.objects.filter(private=False).exclude(owned_by=request.user)
    folders = models.Folder.objects.filter(owned_by=request.user)

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
    else:
        folder_form = FolderForm()
        search_form = SearchForm()

    return render(request, 'fileshare/main.html',
                  {'your_reports': your_reports, 'num_reports': num_reports, 'other_reports': other_reports,
<<<<<<< HEAD
                   'folder_form': folder_form, 'folders': folders})
=======
                   'folder_form': folder_form, 'folders': folders, 'search_form': search_form})
>>>>>>> adc7d5419611a530a734e332e028658e3dbcc86e


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
                private=report_form.cleaned_data['private']
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

    # if(request.user.is_staff == False):
    if report.private and request.user != report.owned_by and request.user.is_staff is False:
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
            
            # elif request.POST.get('action')[0] == "f":
            #     report.last_modified = datetime.datetime.now()
            #     report.last_modified_by = request.user.username
            #     d = get_object_or_404(models.Documents, pk=request.POST.get('action')[1:])
            #     d.delete()

            else:
                report.delete()
                return redirect('main')
    else:
        update_form = ReportForm(instance=report)

    return render(request, 'fileshare/view_report.html', {'report': report, 'update_form': update_form, 'files': files, 'num_files': files.count()})

@login_required
def view_group_report(request, report_id, profilegroup_id):
    report = get_object_or_404(models.Report, pk=report_id)
    group = get_object_or_404(models.ProfileGroup, pk=profilegroup_id)

    if request.user.profile not in group.members.all():
        return redirect('main')




    return render(request, 'fileshare/view_group_report.html', {'report': report, 'group': group})

def user_delete_report(request, report_id):
    report = get_object_or_404(models.Report, pk=report_id)
    report.delete()
    return HttpResponseRedirect('/main')



@login_required(login_url='login')
def account_update_success(request):
    return render(request, 'fileshare/account_update_success.html')


@login_required(login_url='login')
def account(request):
    return render(request, 'fileshare/account.html')


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
                thekey = RSA.importKey(newconvo.sender.profile.publickey)
                messagetoencrypt = request.POST['messagecontent']
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
                                                           messagecontent=request.POST['messagecontent'],
                                                           time=datetime.datetime.now(), key=request.POST['thekey'])
                newmessage2.save()


            return redirect("/messages")

        elif form.is_valid():

            # sender data
            if (request.POST['thekey'] != "True"):
                newmessage = models.Message.objects.create(owned_by=form.cleaned_data['owned_by'],
                                                           sender=user,
                                                           messagecontent=request.POST['messagecontent'],
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

                messagetoencrypt = request.POST['messagecontent']
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
                                                           messagecontent=request.POST['messagecontent'],
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
    return render(request, "fileshare/changepassword.html", context)


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

            members_added = request.POST.getlist('members')
            for m in members_added:
                m = get_object_or_404(models.Profile, pk=m)
                m.groups_in.add(instance)
                instance.members.add(m)

            instance.creator = request.user
            instance.save()
            m.save()

            return redirect('main')  # group made successfully
    else:
        # group_form=GroupForm()
        members = models.Profile.objects.all()

    return render(request, 'fileshare/create_group.html', {'members': members})


@login_required(login_url='login')
def view_group(request, group_id):
    group = get_object_or_404(models.ProfileGroup, pk=group_id)
    #private_reports = request.user.profile.reports_owned.filter(private=True)
    private_reports = models.Report.objects.filter(owned_by=request.user, private=True).exclude(id__in=group.reports.all())
    all_users = models.User.objects.all()

    if request.user.profile not in group.members.all() and not request.user.is_staff:
        return redirect('main')
    elif request.method == "POST":
        update_form = GroupForm(request.POST, instance=group)
        action = request.POST.get('action')
        
        if action != "Save Changes":
            if action[0] == 'a':
                report = get_object_or_404(models.Report, pk=action[1:])
                group.reports.add(report)
                group.save()
            elif action[0] == 'r':
                report = get_object_or_404(models.Report, pk=action[1:])
                group.reports.remove(report)
                group.save()
            
            elif action[0] == 'p':
                m = get_object_or_404(models.Profile, pk=action[1:])
                m.groups_in.add(group)
                group.members.add(m)
                group.save()

            elif action == 'l':
                request.user.profile.groups_in.remove(group)
                group.members.remove(request.user.profile)
                group.save()


            else:
                m = get_object_or_404(models.Profile, pk=action)
                m.groups_in.remove(group)
                group.members.remove(m)
                group.save()

        if update_form.is_valid():

            if request.POST.get('action') == "Save Changes":
                update_form.save()
            else:
                group.delete()
                return redirect('main')
    else:
        update_form = GroupForm(instance=group)

    return render(request, 'fileshare/view_group.html', {'group': group, 'update_form': update_form, 'private_reports': private_reports, 'all_users': all_users})



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
            else:
                folder.reports.remove(report)
                report.in_folder = False
            folder.save()

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


            # return HttpResponseRedirect('/register/success/'+str(newuser.id))
            # return(register_success(request,newuser.id))
            return render(request,'fileshare/register_success.html',{'key':str(key.exportKey())})

    else:
        register_form = signup_form()

    return render(request, 'fileshare/register.html', {'form': signup_form()})

# site manager views
def sitemanager(request):
    if (request.user.is_staff):
        return render(request, 'fileshare/sitemanager.html')


def manage_users(request):
    if (request.user.is_staff):
        all_users = models.User.objects.all()
        return render(request, 'fileshare/manage_users.html', {'all_users': all_users})


def manage_reports(request):
    if (request.user.is_staff):
        all_reports = models.Report.objects.all()
        return render(request, 'fileshare/manage_reports.html', {'all_reports': all_reports})


def manage_groups(request):
    if (request.user.is_staff):
        all_groups = models.ProfileGroup.objects.all()
        return render(request, 'fileshare/manage_groups.html', {'all_groups': all_groups})


def edit_user(request, user_id):
    profile = models.Profile.objects.filter(user_id=user_id)
    # print(profile[0].user.username)
    return render(request, 'fileshare/edit_user.html', {'profile': profile[0]})


def sm_update_user(request):
    profile = models.Profile.objects.filter(pk=request.POST['profile_id'])[0]
    user = profile.user

    user.first_name = request.POST['first_name']
    user.last_name = request.POST['last_name']
    user.email = request.POST['email']
    user.is_active = not request.POST.get('is_active', None) == None
    user.is_staff = not request.POST.get('is_staff', None) == None
    user.save()
    return render(request, 'fileshare/user_update_success.html', {'profile': profile})


def delete_report(request, report_id):
    report = get_object_or_404(models.Report, pk=report_id)
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
