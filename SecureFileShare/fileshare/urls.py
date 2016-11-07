from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings
from . import views
from django.contrib.auth import forms
from django.contrib.auth import views as auth_views
from django.views.generic.edit import CreateView
from fileshare.forms import LoginForm
from .forms import signup_form



# user authentication urls
urlpatterns = [
    #url(r'^register/$', views.register, name='register'),
    url(r'^$', views.main, name='main'),
    url('^register/signup',CreateView.as_view(template_name='fileshare/register.html',form_class=signup_form,success_url='/fileshare/register/success')),
    url('^register/success',views.register_success,name='register_success'),
    url('^login/$',auth_views.login,{'template_name': 'fileshare/login.html', 'authentication_form': LoginForm},name='login'),
    url('^profile', views.profile, name='user_profile'),
    url('^main',views.main,name='main'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/login'}),
    url('^test', CreateView.as_view(template_name='fileshare/test.html',form_class=signup_form,success_url='/fileshare/register/success')),
    #url(r'^test',views.signin,name='signin'),
    #url(r'^',include('django.contrib.auth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)