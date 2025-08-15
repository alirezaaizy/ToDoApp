from django.contrib import admin
from .models import Tag, Todo, Attachment

admin.site.register(Tag)
admin.site.register(Todo)
admin.site.register(Attachment)
