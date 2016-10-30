from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import authenticate
from django.shortcuts import render_to_response
from .forms import UserForm
from django.template import RequestContext
from django.contrib.auth.forms import UserCreationForm


# Create your views here.




def register_success(request):
    return render(request,'fileshare/register_success.html')

def profile(request):
	return

def main(request):
    if not request.user.is_authenticated:
        return redirect('register/login')
    else:
        return render(request,'fileshare/main.html')