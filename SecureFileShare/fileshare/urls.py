from django.conf.urls import include, url
from . import views
from django.contrib.auth import forms
from django.views.generic.edit import CreateView



# user authentication urls
urlpatterns = [
    #url(r'^register/$', views.register, name='register'),
    url(r'^$', views.index, name='index'),
    url('^register/signup',CreateView.as_view(template_name='fileshare/register.html',form_class=forms.UserCreationForm,success_url='/fileshare/register/success')),
    url('^register/success',views.register_success,name='register_success'),
    url('^register/login',CreateView.as_view(template_name='fileshare/register/login.html',form_class=forms.AuthenticationForm,success_url='/fileshare/register/loggedin')),
    url('^profile', views.profile, name='user_profile')
    #url(r'^',include('django.contrib.auth.urls')),
]