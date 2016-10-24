from django.conf.urls import include, url
from . import views
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView



# user authentication urls
urlpatterns = [
    #url(r'^register/$', views.register, name='register'),
    url(r'^$', views.index, name='index'),
    url('^register/',CreateView.as_view(template_name='fileshare/register.html',form_class=UserCreationForm,success_url='/fileshare/register_success')),
    url('^register_success',views.register_success,name='register_success'),
    #url(r'^',include('django.contrib.auth.urls')),
]