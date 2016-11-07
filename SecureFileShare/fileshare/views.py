from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect, QueryDict
from . import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import update_session_auth_hash
from . import models

# Create your views here.

def register_success(request):
    return render(request,'fileshare/register_success.html')

def profile(request):
	return

@login_required(login_url='login')
def main(request):
    return render(request,'fileshare/main.html')

@login_required(login_url='login')
def account_update_success(request):
    return render(request,'fileshare/account_update_success.html')

@login_required(login_url='login')
def account(request):
    return render(request,'fileshare/account.html')

def messages(request):
    conversation_list = models.Conversation.objects.all()
    return render(request,'fileshare/messages.html',{'conversation_list':conversation_list})

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


