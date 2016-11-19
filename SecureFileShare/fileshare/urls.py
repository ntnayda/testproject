from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings
from . import views
from django.contrib.auth import forms
from django.contrib.auth import views as auth_views
from django.views.generic.edit import CreateView
from fileshare.forms import LoginForm
from .forms import signup_form, UpdateProfile
from django.contrib.auth.decorators import permission_required


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
    url('^messages',views.messages, name='messages'),
    url('^create_report',views.create_report,name='create_report'),
    url('^create_group', views.create_group, name='create_group'),
    #url('^account/changepassword',auth_views.password_change,{'template_name':'fileshare/changepassword.html'},name='password_change'),
    #url('^account/changepassworddone',auth_views.password_change,{'template_name':'fileshare/changepassword.html'},name='password_change'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/login'}),
    url('^test', CreateView.as_view(template_name='fileshare/test.html',form_class=signup_form,success_url='/fileshare/register/success')),
    #url(r'^test',views.signin,name='signin'),
    #url(r'^',include('django.contrib.auth.urls')),
    url('^test', views.update_profile, name='updateprofile'),
    url(r'^(?P<report_id>[0-9]+)/view/$', views.view_report, name='view_report'),
    url(r'^(?P<group_id>[0-9]+)/view_group/$', views.view_group, name='view_group'),
    url('^test', views.update_profile,name='updateprofile'),
    url('^deletemessage/(?P<message_pk>.*)$',views.deletemessage,name="delete_message"),
    url('^sitemanager', permission_required('is_superuser')(views.sitemanager), name='sitemanager'),
    url('^users', permission_required('is_superuser')(views.users), name='users'),
]