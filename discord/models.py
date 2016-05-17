from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Game(models.Model):
	name = models.TextField()

class User(models.Model):
	username = models.CharField(max_length=64)
	avatar = models.CharField(max_length=64, null=True, blank=True)
	id = models.CharField(max_length=64, primary_key=True)

class Guild(models.Model):
	id = models.CharField(max_length=64, primary_key=True)
	name = models.CharField(max_length=100)
	icon = models.CharField(max_length=64, null=True, blank=True)
	game = models.ForeignKey(Game, on_delete=models.SET_NULL, blank=True, null=True)

class Channel(models.Model):
	id = models.CharField(max_length=64, primary_key=True)
	guild = models.ForeignKey(Guild, on_delete=models.CASCADE)
	name = models.CharField(max_length=100)

class Message(models.Model):
	id = models.CharField(max_length=64,primary_key=True)
	channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
	post_date = models.DateTimeField('Date Posted')
	last_edit = models.DateTimeField('Last Edit Date', null=True, blank=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	content = models.TextField()

class Attachment(models.Model):
	id = models.CharField(max_length=64,primary_key=True)
	message = models.ForeignKey(Message, on_delete=models.CASCADE)
	is_image = models.BooleanField(default=False)
	url = models.URLField()
	height = models.IntegerField(default=0)
	width = models.IntegerField(default=0)
	proxy_url = models.URLField()
	name = models.CharField(max_length=255)