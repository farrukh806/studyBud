from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from .models import Room, Topic
from .forms import RoomForm


def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Username or password is incorrect')
        except:
            messages.error(request, 'User does not exist')

    return render(request, 'register_login.html')

def logoutUser(request):
    logout(request)
    return redirect('home')

def home(request):
    query = request.GET.get('q')
    
    if query == None:
        query = ''
    rooms = Room.objects.filter(Q(topic__name__icontains=query) | Q(name__icontains=query)| Q(description__icontains=query))
    topics = Topic.objects.all()
    context = {'rooms': rooms, 'topics': topics, 'rooms_count':rooms.count()}
    return render(request, 'home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
   
    context = {'room': room}
    return render(request, 'room.html', context)

def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'room_form.html', context)

def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = { 'form' : form }
    return render(request, 'room_form.html', context)

def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    print('delete route')
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'delete.html', {'obj':room})