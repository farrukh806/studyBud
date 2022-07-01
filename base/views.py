from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm


def loginPage(request):
    page = 'Login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Hello ' + user.get_username())
                return redirect('home')
            else:
                messages.error(request, 'Username or password is incorrect')
        except:
            messages.error(request, 'User does not exist')

    context = {'page': page}
    return render(request, 'register_login.html', context)


def registerPage(request):
    page = 'Register'
    form = UserCreationForm()
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            messages.success(request, 'Hello ' + user.get_username())
            return redirect('home')
        else:
            messages.error(request, 'Something went wrong!')
    
    context = {'page': page, 'form': form}
    return render(request, 'register_login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def home(request):
    query = request.GET.get('q')
    
    if query == None:
        query = ''
    rooms = Room.objects.filter(Q(topic__name__icontains=query) | Q(name__icontains=query)| Q(description__icontains=query))
   
    topics = Topic.objects.all()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=query))
    context = {'rooms': rooms, 'topics': topics, 'rooms_count':rooms.count(), 'room_messages': room_messages}
   
    return render(request, 'home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(user=request.user, room=room, body=request.POST.get('body'))
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {'room': room, 'room_messages':room_messages, 'participants':participants}
    return render(request, 'room.html', context)


def userProfile(request, pk):
    try:
        user = User.objects.get(id=pk)
        rooms = user.room_set.all()
        room_messages = user.message_set.all()
        topics = Topic.objects.all()
        if user is not None:
            context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
            return render(request, 'profile.html', context)
        else:
            return redirect('home')
    except:
        return redirect('home')
    
  
    

@login_required(login_url='/login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        form = RoomForm(request.POST)
        Room.objects.create(
            host = request.user, 
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
        return redirect('home')
        
    context = {'form': form, 'topics': topics}
    return render(request, 'room_form.html', context)


@login_required(login_url='/login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user.id != room.host.id:
        return HttpResponse('Access Denied!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('/room/' + str(room.id))
    context = { 'form' : form, 'topics': topics, 'room': room}
    return render(request, 'room_form.html', context)


@login_required(login_url='/login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user.id != room.host.id:
        return HttpResponse('Access Denied!')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'delete.html', {'obj':room})


@login_required(login_url='/login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
   
    if request.user != message.user:
        return HttpResponse('Access Denied!')
    
    if request.method == 'POST':
        message.delete()
        return redirect('/room/' + str(message.room.id))
    return render(request, 'delete.html', {'obj':message})