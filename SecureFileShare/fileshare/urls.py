from django.conf.urls import include, url
from . import views
from django.contrib.auth import forms
from django.contrib.auth import views as auth_views
from django.views.generic.edit import CreateView
from fileshare.forms import LoginForm
from .forms import signup_form, UpdateProfile



# user authentication urls
urlpatterns = [
    url(r'^$', views.main, name='main'),
    url('^register/signup',CreateView.as_view(template_name='fileshare/register.html',form_class=signup_form,success_url='/fileshare/register/success')),
    url('^register/success',views.register_success,name='register_success'),
    url('^register/updateprofile/success',views.account_update_success,name='account_update_success'),
    url('^login/$',auth_views.login,{'template_name': 'fileshare/login.html', 'authentication_form': LoginForm},name='login'),
    url('^profile', views.profile, name='user_profile'),
    url('^main',views.main,name='main'),
    url('^account/view',views.account,name='account'),
    url('^account/update',views.update_profile,name='accountupdate'),
    url('^account/changepassword',views.password_change,name='password_change'),
    url('^messages',views.messages,name='messages'),
    #url('^account/changepassword',auth_views.password_change,{'template_name':'fileshare/changepassword.html'},name='password_change'),
    #url('^account/changepassworddone',auth_views.password_change,{'template_name':'fileshare/changepassword.html'},name='password_change'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/login'}),
    url('^test', views.update_profile,name='updateprofile'),
]