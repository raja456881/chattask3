from channels.generic.websocket import WebsocketConsumer
from channels.consumer import AsyncConsumer
from asgiref.sync import async_to_sync
import json
from django.core.validators import ValidationError
from .models import User
from .models import Thread, Message, BroadcastNotification, Noficationmessage
from django.contrib.auth.models import Group

from channels.auth import login

class chatroom(WebsocketConsumer,AsyncConsumer, Thread):
    def connect(self):
            self.room_name = self.scope['url_route']['kwargs']['username']
            other_username=self.scope['url_route']['kwargs']['username']
            self.room_group_name = 'room_%s' % self.room_name
            me = self.scope['user']

            other_user=User.objects.get(username=other_username)
            self.thread_obj=Thread.objects.get_or_create_personal_thread(me, other_user)
            self.room_name=f'personal_thread_{self.thread_obj.id}'
            self.update_user_status(me, 'online')
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            self.accept()

    def disconnect(self, close_code):
        user = self.scope['user']
        self.update_user_status(user, 'offline')

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {
                'type':'chat_message',
                'message': text_data,
            }
        )

    def chat_message(self, event):
        message = event['message']
        data = json.loads(message)
        user=self.scope['user']
        id=User.objects.get(username=user)
        id1=id.id
        self.store_message(data['message'])
        self.send(text_data=json.dumps({
            'message': data['message'],
            'image':data['image'],
            'video':data['video'],
            'id':id1

        }))
    def update_user_status(self, user, status):
        return User.objects.filter(pk=user.pk).update(status=status)

    def store_message(self, text):
        Message.objects.create(
            thread=self.thread_obj,
            sender=self.scope['user'],
            text=text
        )

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.list=[]
        group = self.scope['url_route']['kwargs']['groupname']
        self.room_name=group
        async_to_sync(self.channel_layer.group_add)(self.room_name, self.channel_name)
        print(f'{self.channel_name}')
        user = self.scope['user']
        user1 = user.groups.filter(name=group).exists()
        if user1 is False:
            return self.disconnect(close_code=None)
        self.accept()

    def disconnect(self, close_code):
        group = self.scope['url_route']['kwargs']['groupname']
        self.room_name=group
        print(f'{self.channel_name}  User is not Exists in {group}')
        async_to_sync(self.channel_layer.group_discard)(self.room_name, self.channel_name)

    def receive(self, text_data):
        print(text_data)
        async_to_sync(self.channel_layer.group_send)(
            self.room_name,
            {
             'type':'chat_message1',
            'message': text_data,
            }
        )

    def chat_message1(self, event):
        message = event['message']
        data = json.loads(message)
        self.list.append({"message":data['message']})
        print(self.list)
        user=self.scope['user']
        id = User.objects.get(username=user)
        id1 = id.id
        reciver_user_id=data['id']
        print(reciver_user_id)
        self.send_noficatication(data, user)
        self.send(text_data=json.dumps({
        'message':self.list,
        'image': data['image'],
        'video': data['video'],
            'id': id1

    }))

    def send_noficatication(self, data, user):
        return Noficationmessage.objects.create(user=user, message=data['message'], video=data['video'], image=data['image'])



    async def send_notification(self, event):
        message = json.loads(event['message'])

        # Send message to WebSocket
        await self.send(text_data=json.dumps(message))

