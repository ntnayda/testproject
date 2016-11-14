from django.conf.urls import include, url
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static




urlpatterns = [
    # Examples:
    # url(r'^$', 'SecureFileShare.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^fileshare/',include('fileshare.urls', namespace="fileshare")),
    url(r'^',include('fileshare.urls')),
    url(r'^accounts/profile',RedirectView.as_view(url='/main')),
    #url(r'^',include('django.contrib.auth.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
