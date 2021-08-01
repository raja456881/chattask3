from django.contrib import admin
from.models import Thread, User, Message,BroadcastNotification, Noficationmessage
# Register your models here.
admin.site.register(Thread)
admin.site.register(User)
admin.site.register(Message)
admin.site.register(BroadcastNotification)
admin.site.register(Noficationmessage)