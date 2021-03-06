from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.db.models import Q
from re import split as re_split
import datetime
import urllib

from .models import Guild, Channel, User, Message, Game, Attachment

def parse_time(timestamp):
	if timestamp:
		return datetime.datetime(*map(int, re_split(r'[^\d]', timestamp.replace('+00:00', ''))))
	return None

# Create your views here.
def index(request):
	games = Game.objects.order_by('name')
	misc = Guild.objects.filter(game__isnull=True)
	context = {'game_list': games, 'misc': misc}
	return render(request, 'discord/index.html', context)

def guild(request, guild):
	g = Guild.objects.get(id=guild)
	context = {'channels': g.channel_set.order_by('name'), 'guild': Guild.objects.get(id=guild)}
	return render(request, 'discord/guild.html', context)

def channel(request, guild, channel, page):
	g = Guild.objects.get(id=guild)
	c = g.channel_set.get(id=channel)
	last = (((len(c.message_set.values())-1)/50)+1)
	blist = [i for i in range(1, int(page))][-5:]
	flist = [i for i in range(int(page)+1, last+1)][:5]
	messages = c.message_set.order_by('post_date')[50*(int(page)-1):50*(int(page))]
	for message in messages:
		if "<@" in message.content:
			for word in message.content.split(" "):
				if "<@" in word:
					userid = word[2:-1]
					users = User.objects.filter(id=userid) 
					if len(users) == 1:
						message.content = message.content.replace(word, "@" + users[0].username)
		if "<#" in message.content:
			for word in message.content.split(" "):
				if "<#" in word:
					channelid = word[2:-1]
					channels = Channel.objects.filter(id=channelid) 
					if len(channels) == 1:
						message.content = message.content.replace(word, "#" + channels[0].name)
		#message.content = message.content.replace("<", "&lt;").replace(">", "&gt;")
	context = {'messages': messages, 'guild':g, 'channel':c, 'page':page, 'last':str(last), 'prev':int(page)-1, 'next':int(page)+1, 'blist':blist, 'flist':flist}
	return render(request, 'discord/channel.html', context)

def jump(request, guild, channel, page):
	try:
		p = request.POST['page']
	except (KeyError):
		return HttpResponse(status=404)
	else:
		return HttpResponseRedirect(reverse('discord:channel', args=(guild, channel, p,)))

def searchuser(request, user, page):
	#Render page with search results
	results = Message.objects.filter(user__id=user).order_by('-post_date')
	
	last = (((len(results)-1)/50)+1)
	blist = [i for i in range(1, int(page))][-5:]
	flist = [i for i in range(int(page)+1, last+1)][:5]
	messages = results[50*(int(page)-1):50*(int(page))]
	for message in messages:
		if "<@" in message.content:
			for word in message.content.split(" "):
				if "<@" in word:
					userid = word[2:-1]
					users = User.objects.filter(id=userid) 
					if len(users) == 1:
						message.content = message.content.replace(word, "@" + users[0].username)
		if "<#" in message.content:
			for word in message.content.split(" "):
				if "<#" in word:
					channelid = word[2:-1]
					channels = Channel.objects.filter(id=channelid) 
					if len(channels) == 1:
						message.content = message.content.replace(word, "#" + channels[0].name)
	
	context = {'messages': messages, 'page':page, 'last':str(last), 'prev':int(page)-1, 'next':int(page)+1, 'blist':blist, 'flist':flist, 'searched': True, 'total': len(results), 'guilds': Guild.objects.all(), 'query': urllib.urlencode(request.GET), 'userid': user}
	return render(request, 'discord/user.html', context)

def search(request, page):
	if 'querytext' in request.GET:
		#Render page with search results
		querytext = request.GET['querytext'] if 'querytext' in request.GET else None
		channels = request.GET['channel'] if 'channel' in request.GET else None
		guilds = request.GET['guild'] if 'guild' in request.GET else None
		games = request.GET['game'] if 'game' in request.GET else None
		users = request.GET['user'] if 'user' in request.GET else None
		
		query = Q()
		if querytext:
			query = Q(content__contains="" + querytext + "")
		
		if channels:
			q = Q()
			for channel in channels.split("+"):
				q = q | Q(channel__id=channel)
			query = query & q
		if guilds:
			q = Q()
			for guild in guilds.split("+"):
				q = q | Q(channel__guild__id=guild)
			query = query & q
		if games:
			q = Q()
			for game in games.split("+"):
				q = q | Q(channel__guild__game__id=game)
			query = query & q
		if users:
			q = Q()
			for user in users.split("+"):
				q = q | Q(user__username=user)
			query = query & q
		results = Message.objects.filter(query).order_by('-post_date')
		
		last = (((len(results)-1)/50)+1)
		blist = [i for i in range(1, int(page))][-5:]
		flist = [i for i in range(int(page)+1, last+1)][:5]
		messages = results[50*(int(page)-1):50*(int(page))]
		for message in messages:
			if "<@" in message.content:
				for word in message.content.split(" "):
					if "<@" in word:
						userid = word[2:-1]
						users = User.objects.filter(id=userid) 
						if len(users) == 1:
							message.content = message.content.replace(word, "@" + users[0].username)
			if "<#" in message.content:
				for word in message.content.split(" "):
					if "<#" in word:
						channelid = word[2:-1]
						channels = Channel.objects.filter(id=channelid) 
						if len(channels) == 1:
							message.content = message.content.replace(word, "#" + channels[0].name)
			#AAAAAAAAA
			message.content = message.content.replace("<", "&lt;").replace(">", "&gt;")
			message.content = message.content.replace("" + querytext + "", "<b>" + querytext + "</b>")
		
		pages = []
		"""for result in results:
			channel = result.channel
			index = channel.message_set.filter(post_date__lt = result.post_date).count()
			page = index/50+1
			asdf = "<a href='http://localhost:8000/discord/"+str(channel.guild.id)+"/"+str(channel.id)+"/"+str(page)+"/#"+str(result.id)+"'>Link</a>"
			pages.append((result.id, result.content, asdf))"""
		#context = {"message": pages}
		#return render(request, 'discord/results.html', context)
		#return HttpResponse(str(pages))
		context = {'messages': messages, 'page':page, 'last':str(last), 'prev':int(page)-1, 'next':int(page)+1, 'blist':blist, 'flist':flist, 'searched': True, 'total': len(results), 'guilds': Guild.objects.all(), 'query': urllib.urlencode(request.GET)}
		return render(request, 'discord/search.html', context)
	else:
		#Render the page without any results
		#return render(request, 'discord/results.html', {})
		return render(request, 'discord/search.html', {'guilds': Guild.objects.all(), 'searched': False})

def searchhome(request):
	return render(request, 'discord/search.html', {'guilds': Guild.objects.all(), 'searched': False})

def find(request, guild, channel, message):
	m = get_object_or_404(Message, id=message)
	c = get_object_or_404(Channel, id=channel)
	index = c.message_set.filter(post_date__lt = m.post_date).count()
	page = index/50+1
	return HttpResponseRedirect(reverse('discord:channel', args=(guild, channel, page,)) + "#" + str(message))

def latest(request, channel):
	c = get_object_or_404(Channel, id=channel)
	message = c.message_set.order_by('-post_date')[0]
	return HttpResponse(str(message.id))

@csrf_exempt
def update(request):
	if 'type' in request.POST:
		type = request.POST['type']
		if type == 'guild':
			id = request.POST['id']
			name = request.POST['name']
			icon = request.POST['icon']
			guild = Guild.objects.filter(id=id)
			if len(guild) == 1:
				guild = guild[0]
				guild.name = name
				guild.icon = icon
				guild.save()
				return HttpResponse(status=201)
			return HttpResponse(status=409)
		elif type == 'channel':
			id = request.POST['id']
			name = request.POST['name']
			channel = Channel.objects.filter(id=id)
			if len(channel) == 1:
				channel = channel[0]
				channel.name = name
				channel.save()
				return HttpResponse(status=201)
			return HttpResponse(status=409)
		elif type == 'user':
			id = request.POST['id']
			username = request.POST['username']
			avatar = request.POST['avatar']
			user = User.objects.filter(id=id)
			if len(user) == 1:
				user = user[0]
				user.username = username
				user.avatar = avatar
				user.save()
				return HttpResponse(status=201)
			return HttpResponse(status=409)
		elif type == 'message':
			id = request.POST['id']
			content = request.POST['content']
			edited = parse_time(request.POST['edited'])
			message = Message.objects.filter(id=id)
			if len(message) == 1:
				message = message[0]
				message.content = content
				message.last_edit = edited
				message.save()
				return HttpResponse(status=201)
			return HttpResponse(status=409)
		elif type == 'messagedelete':
			id = request.POST['id']
			message = Message.objects.filter(id=id)
			if len(message) == 1:
				message = message[0]
				message.delete()
				return HttpResponse(status=201)
			return HttpResponse(status=409)

@csrf_exempt
def create(request):
	if 'type' in request.POST:
		type = request.POST['type']
		if type == 'guild':
			id = request.POST['id']
			name = request.POST['name']
			icon = request.POST['icon']
			if not Guild.objects.filter(id=id).exists():
				guild = Guild(id=id, name=name, icon=icon)
				guild.save()
				return HttpResponse(status=201)
			return HttpResponse(status=409)
		elif type == 'channel':
			id = request.POST['id']
			name = request.POST['name']
			g = request.POST['guild']
			if Channel.objects.filter(id=id).exists():
				return HttpResponse(status=409)
			if Guild.objects.filter(id=g).exists():
				guild = Guild.objects.get(id=g)
				guild.channel_set.create(id=id, name=name)
				return HttpResponse(status=201)
			return HttpResponse(status=424)
		elif type == 'user':
			id = request.POST['id']
			username = request.POST['username']
			avatar = request.POST['avatar']
			if not User.objects.filter(id=id).exists():
				user = User(id=id, username=username, avatar=avatar)
				user.save()
				return HttpResponse(status=201)
			return HttpResponse(status=409)
		elif type == 'message':
			id = request.POST['id']
			channel = request.POST['channel']
			user = request.POST['user']
			content = request.POST['content']
			timestamp = parse_time(request.POST['timestamp'])
			edited = parse_time(request.POST['edited'])
			if Message.objects.filter(id=id).exists():
				return HttpResponse(status=409)
			if (Channel.objects.filter(id=channel).exists()) and (User.objects.filter(id=user).exists()):
				channel = Channel.objects.get(id=channel)
				user = User.objects.get(id=user)
				channel.message_set.create(id=id, user=user, post_date=timestamp, last_edit=edited, content=content)
				return HttpResponse(status=201)
			return HttpResponse(status=424)
		elif type == 'attachment':
			id = request.POST['id']
			name = request.POST['name']
			url = request.POST['url']
			proxy_url = request.POST['proxy_url']
			if str(name).lower().split(".")[-1] in ["jpg", "png", "gif", "jpeg"]:
				is_image = True
				height = int(request.POST['height'])
				width = int(request.POST['width'])
				if height > width:
					if height > 500:
						width = int(width * 500.0 / height)
						height = 500
				else:
					if width > 500:
						height = int(height * 500.0 / width)
						width = 500	
			else:
				is_image = False
				height = 0
				width = 0
			message = request.POST['message']
			if Attachment.objects.filter(id=id).exists():
				return HttpResponse(status=409)
			if Message.objects.filter(id=message).exists():
				message = Message.objects.get(id=message)
				message.attachment_set.create(id=id, name=name, url=url, proxy_url=proxy_url, is_image=is_image, height=height, width=width)
				return HttpResponse(status=201)
			return HttpResponse(status=424)
		else:
			raise Http404("Invalid Request")

