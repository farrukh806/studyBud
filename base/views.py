import imp
import re
from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Room, Topic
from .forms import RoomForm
# Create your views here.

# rooms = []
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