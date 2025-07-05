from datetime import datetime
from channels.layers import get_channel_layer
import json
from asgiref.sync import async_to_sync


def message_from_outside_consumer(conversation, sender, message_text, media_id=None, media_type=None, contacts=None, media_url=None):
    channel_layer = get_channel_layer()

    group_name = f'user_{conversation.user.id}_chat'

    # payload = {
    #     "text": message_text,      # can be text or caption
    #     "sender": sender,
    #     'conversation_id':  conversation.id,
    # }

    # if media_id:
    #     payload["media_id"] = media_id

    # if media_type:
    #     payload["media_type"] = media_type

    # if contacts:
    #     payload['contacts'] = contacts

    # if media_url:
    #     payload['media_url'] = media_url

    # print("comming.... ======================= websocket service =================")
    # print("payload", payload)

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'chat.message',  # must match method name 'chat_message' in consumer
            'message': json.dumps({
                "conversation_id": str(conversation.id),
                "message": {
                    "id": f"ws-{int(datetime.now().timestamp() * 1000)}",
                    "text": message_text,
                    "time": datetime.now().isoformat(),
                    "sender": sender,
                    "media_id": media_id,
                    "media_url": media_url,
                    "media_type": media_type,
                    "contacts": contacts or [],
                    # "conversation_id": str(conversation.id),
                }

            })
        }
    )

    # await self.channel_layer.group_send(
    #     self.group_name,
    #     {
    #         'type': 'chat.message',
    #         'message': json.dumps({
    #             # Ensure string type
    #             "conversation_id": str(conversation_id),
    #             "message": {
    #                 "id": f"ws-{int(datetime.now().timestamp() * 1000)}",
    #                 "text": message_text,
    #                 "time": datetime.now().isoformat(),
    #                 "sender": "business",  # or determine dynamically
    #                 "media_id": payload.get('media_id'),
    #                 "media_url": payload.get('media_url'),
    #                 "media_type": payload.get('media_type'),
    #                 "contacts": payload.get('contacts', []),
    #                 "conversation_id": str(conversation_id),
    #             }}),
    #         'sender_channel': self.channel_name
    #     }
    # )
