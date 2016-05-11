from django.conf.urls import url

from . import views

app_name = 'discord'
urlpatterns = [
	url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^(?P<guild>[0-9]+)/$', views.guild, name='guild'),
	url(r'^(?P<guild>[0-9]+)/(?P<channel>[0-9]+)/(?P<page>[0-9]+)/$', views.channel, name='channel'),
	url(r'^create/$', views.create, name='create'),
	url(r'^(?P<guild>[0-9]+)/(?P<channel>[0-9]+)/(?P<page>[0-9]+)/jump/$', views.jump, name='jump'),
]
