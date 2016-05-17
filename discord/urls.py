from django.conf.urls import url

from . import views

app_name = 'discord'
urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^(?P<guild>[0-9]+)/$', views.guild, name='guild'),
	url(r'^(?P<guild>[0-9]+)/(?P<channel>[0-9]+)/(?P<page>[0-9]+)/$', views.channel, name='channel'),
	url(r'^create/$', views.create, name='create'),
	url(r'^update/$', views.update, name='update'),
	url(r'^(?P<guild>[0-9]+)/(?P<channel>[0-9]+)/(?P<page>[0-9]+)/jump/$', views.jump, name='jump'),
	url(r'^(?P<channel>[0-9]+)/latest/$', views.latest, name='latest'),
]
