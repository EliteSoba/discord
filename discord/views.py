from django.shortcuts import get_object_or_404, render
from django.views import generic
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from re import split as re_split
import datetime

from .models import Guild, Channel, User, Message

def parse_time(timestamp):
	if timestamp:
		return datetime.datetime(*map(int, re_split(r'[^\d]', timestamp.replace('+00:00', ''))))
	return None

# Create your views here.

class IndexView(generic.ListView):
	template_name = 'discord/index.html'
	context_object_name = 'guild_list'
	
	def get_queryset(self):
		return Guild.objects.order_by('name')

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
	messages = c.message_set.order_by('id')[50*(int(page)-1):50*(int(page))]
	for message in messages:
		if "<@" in message.content:
			for word in message.content.split(" "):
				if "<@" in word:
					userid = word[2:-1]
					users = User.objects.filter(id=userid) 
					if len(users) == 1:
						message.content = message.content.replace(word, "@" + users[0].username)
	context = {'messages': messages, 'guild':g, 'channel':c, 'page':page, 'last':last, 'prev':int(page)-1, 'next':int(page)+1, 'blist':blist, 'flist':flist}
	return render(request, 'discord/channel.html', context)

def jump(request, guild, channel, page):
	try:
		p = request.POST['page']
	except (KeyError):
		return HttpResponse(status=404)
	else:
		return HttpResponseRedirect(reverse('discord:channel', args=(guild, channel, p,)))

def latest(request, channel):
	c = get_object_or_404(Channel, id=channel)
	message = c.message_set.order_by('-id')[0]
	return HttpResponse(str(message.id))

@csrf_exempt
def create(request):
	if 'type' in request.POST:
		type = request.POST['type']
		if type == 'guild':
			id = request.POST['id']
			name = request.POST['name']
			icon = request.POST['icon']
			if len(Guild.objects.filter(id=id)) < 1:
				guild = Guild(id=id, name=name, icon=icon)
				guild.save()
				return HttpResponse(status=201)
			return HttpResponse(status=403)
		elif type == 'channel':
			id = request.POST['id']
			name = request.POST['name']
			g = request.POST['guild']
			if (len(Channel.objects.filter(id=id)) < 1) and (len(Guild.objects.filter(id=g)) == 1):
				guild = Guild.objects.get(id=g)
				guild.channel_set.create(id=id, name=name)
				return HttpResponse(status=201)
			return HttpResponse(status=403)
		elif type == 'user':
			id = request.POST['id']
			username = request.POST['username']
			avatar = request.POST['avatar']
			if len(User.objects.filter(id=id)) < 1:
				user = User(id=id, username=username, avatar=avatar)
				user.save()
				return HttpResponse(status=201)
			return HttpResponse(status=403)
		elif type == 'message':
			id = request.POST['id']
			channel = request.POST['channel']
			user = request.POST['user']
			content = request.POST['content']
			timestamp = parse_time(request.POST['timestamp'])
			edited = parse_time(request.POST['edited'])
			if len(Message.objects.filter(id=id)) < 1 and len(Channel.objects.filter(id=channel)) == 1 and len(User.objects.filter(id=user)) == 1:
				channel = Channel.objects.get(id=channel)
				user = User.objects.get(id=user)
				channel.message_set.create(id=id, user=user, post_date=timestamp, last_edit=edited, content=content)
				return HttpResponse(status=201)
			return HttpResponse(status=403)
		else:
			raise Http404("Invalid Request")

