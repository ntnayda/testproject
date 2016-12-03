from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings
from . import views
from django.contrib.auth import forms
from django.contrib.auth import views as auth_views
from django.views.generic.edit import CreateView
from fileshare.forms import LoginForm
from .forms import signup_form, UpdateProfile


# user authentication urls
urlpatterns = [
    url(r'^$', views.main, name='main'),
    url('^register/signup',views.register,name='register'),
    url('^register/signup',CreateView.as_view(template_name='fileshare/register.html',form_class=signup_form,success_url='/fileshare/register/success')),
    url('^register/success',views.register_success,name='register_success'),
    url('^register/updateprofile/success',views.account_update_success,name='account_update_success'),
    url('^login/$',auth_views.login,{'template_name': 'fileshare/login.html', 'authentication_form': LoginForm},name='login'),
    url('^main',views.main,name='main'),
    url('^account/view',views.account,name='account'),
    url('^account/update',views.update_profile,name='accountupdate'),
    url('^account/changepassword',views.password_change,name='password_change'),
    url('^messages',views.messages, name='messages'),
    url('^create_report',views.create_report,name='create_report'),
    url(r'^user_delete_report/(?P<report_id>[0-9]+)$', views.user_delete_report, name='user_delete_report'),
    url('^create_group', views.create_group, name='create_group'),
    #url('^account/changepassword',auth_views.password_change,{'template_name':'fileshare/changepassword.html'},name='password_change'),
    #url('^account/changepassworddone',auth_views.password_change,{'template_name':'fileshare/changepassword.html'},name='password_change'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/login'}),
    #url('^test', CreateView.as_view(template_name='fileshare/test.html',form_class=signup_form,success_url='/fileshare/register/success')),
    #url(r'^test',views.signin,name='signin'),
    #url(r'^',include('django.contrib.auth.urls')),
    url('^test', views.test, name='test'),
    url(r'^(?P<report_id>[0-9]+)/view/$', views.view_report, name='view_report'),
    url(r'^view_report/(?P<report_id>[0-9]+)$', views.view_report, name='view_report'),
    url(r'^view_group_report/(?P<report_id>[0-9]+)/(?P<profilegroup_id>[0-9]+)$', views.view_group_report, name='view_group_report'),
    url(r'^(?P<group_id>[0-9]+)/view_group/$', views.view_group, name='view_group'),
    url(r'^(?P<folder_id>[0-9]+)/view_folder/$', views.view_folder, name='view_folder'),
    url('^test', views.update_profile,name='updateprofile'),
    url('^deletemessage/(?P<message_pk>.*)$',views.deletemessage,name="delete_message"),
    #site manager urls
    url('^sitemanager',views.sitemanager, name='sitemanager'),
    url('^manage_users',views.manage_users, name='manage_users'),
    url('^manage_reports', views.manage_reports, name='manage_reports'),
    url('^manage_groups', views.manage_groups, name='manage_groups'),
    url('^edit_user/(?P<user_id>[0-9]+)', views.edit_user, name='edit_user'),
    url('^edit_user', views.edit_user, name='edit_user'),
    url('^sm_update_user', views.sm_update_user, name='sm_update_user'),
    url('^user_update_success.html', views.sm_update_user, name = 'user_update_success'),
    url(r'^delete_report/(?P<report_id>[0-9]+)$', views.delete_report, name='delete_report'),
    url('^decrypt_message/(?P<message_pk>.*)$',views.decrypt_message,name="decrypt_message"),
    url('^update_unread/(?P<message_pk>.*)$',views.updateunread,name="update_unread"),
    url('^search_results', views.search_results, name='search_results'),
]