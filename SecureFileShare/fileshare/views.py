from django.shortcuts import render
from django.shortcuts import render_to_response
from .forms import UserForm
from django.template import RequestContext
from django.contrib.auth.forms import UserCreationForm


# Create your views here.



def index(request):

    return render(request,'fileshare/index.html')

def register_success(request):
    return render(request,'fileshare/register_success.html')