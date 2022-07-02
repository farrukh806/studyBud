from django.contrib import admin

# Register your models here.

from .models import Room, Topic, Message, User

admin.site.register([Room, Topic, Message, User])