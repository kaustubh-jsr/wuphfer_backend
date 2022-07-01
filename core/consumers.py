import json
from channels.generic.websocket import WebsocketConsumer
from .models import *
from asgiref.sync import async_to_sync,sync_to_async
from django.contrib.sessions.backends.db import SessionStore
from urllib.parse import parse_qs

class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        auth_token =parse_qs(self.scope["query_string"].decode("utf-8"))['token'][0]
        print('connected')
        # try:
        session = SessionStore(session_key=auth_token)
        user = User.objects.get(username=session['user_details']['username'])
        self.me = user
        self.room_group_name = f'user_{self.me}'
        print(f'connected to room : {self.room_group_name}')
        self.accept()
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        # except:
        #     print('invalid user, closing connection')
        #     self.disconnect(0)
    
    def receive(self,text_data):
        # self.send(text_data=json.dumps({'message_back':text_data}))
        text_data_json = json.loads(text_data)
        if 'action' in text_data_json and text_data_json['action'] == 'disconnect':
            self.close()
        pass
    
    def disconnect(self,close_code):
        print('disconnected')
        async_to_sync(self.channel_layer.group_discard)(
           self.room_group_name,
           self.channel_name
        )
        self.close()
        print('discarded group')
    
    def notification_send(self,event):
        print('send notification')
        print(event)
        self.send(text_data=json.dumps({'notification':event.get('value')}))




# class NotificationConsumer(WebsocketConsumer):
#     def connect(self):
#         # get user token to get the user
#         auth_token = self.scope['url_route']['kwargs']['token']
#         print('connected to notifications consumer')
#         session = SessionStore(session_key=auth_token)
#         user = User.objects.get(username=session['user_details']['username'])
#         self.me = user
#         self.room_name = f'{self.me}'
#         self.room_group_name = f'notifications_{self.room_name}'
#         print('connect notification')
#         self.accept()

#     def disconnect(self, close_code):
#         pass

#     def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         notification = text_data_json['notification']

#         self.send(text_data=json.dumps({
#             'notification': notification
#         }))