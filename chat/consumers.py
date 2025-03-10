from channels.generic.websocket import AsyncWebsocketConsumer
import json
from datetime import datetime
import uuid

class ChatConsumer(AsyncWebsocketConsumer):
    # Class variable to store all connected users
    connected_users = {}

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        # Generate unique ID for new user
        self.user_id = str(uuid.uuid4())[:8]

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Store user information
        self.connected_users[self.user_id] = {
            'channel_name': self.channel_name,
            'room': self.room_name
        }

        await self.accept()

        # Send the user their ID
        await self.send(json.dumps({
            'type': 'user_info',
            'user_id': self.user_id
        }))

        # Notify others that a new user has joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user_id': self.user_id,
                'users': list(self.connected_users.keys())
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'user_id'):
            # Remove user from connected users
            self.connected_users.pop(self.user_id, None)

            # Notify others that user has left
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left',
                    'user_id': self.user_id,
                    'users': list(self.connected_users.keys())
                }
            )

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user_id': self.user_id,
                'timestamp': datetime.now().strftime("%H:%M")
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'user_id': event['user_id'],
            'timestamp': event['timestamp']
        }))

    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'user_id': event['user_id'],
            'users': event['users']
        }))

    async def user_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'user_id': event['user_id'],
            'users': event['users']
        })) 