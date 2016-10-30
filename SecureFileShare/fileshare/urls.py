from django.conf.urls import include, url
from . import views
from django.contrib.auth import forms
from django.contrib.auth import views as auth_views
from django.views.generic.edit import CreateView



# user authentication urls
urlpatterns = [
    #url(r'^register/$', views.register, name='register'),
    url(r'^$', views.main, name='main'),
    url('^register/signup',CreateView.as_view(template_name='fileshare/register.html',form_class=forms.UserCreationForm,success_url='/fileshare/register/success')),
    url('^register/success',views.register_success,name='register_success'),
    url('^register/login',auth_views.login,{'template_name': 'fileshare/login.html'},name='login'),
    url('^profile', views.profile, name='user_profile'),
    url('^main',views.main,name='main'),
url(r'^logout/$', auth_views.logout, {'template_name': 'fileshare/main.html'}, name='logout'),
    #url(r'^',include('django.contrib.auth.urls')),
]