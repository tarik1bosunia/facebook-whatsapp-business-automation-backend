from channels.layers import get_channel_layer
import json
from asgiref.sync import async_to_sync

def message_from_outside_consumer(conversation_id, sender, message, media_id=None, media_type=None, contacts=None, media_url=None):
    channel_layer = get_channel_layer()

    group_name = 'global_chat'

    payload = {
        "text": message,      # can be text or caption 
        "sender": sender,
        'conversation_id':  conversation_id,
    }

    if media_id:
        payload["media_id"] = media_id

    if media_type:
        payload["media_type"] = media_type

    if contacts:
        payload['contacts'] = contacts

    if media_url:
        payload['media_url'] = media_url  

    print("comming.... ======================= websocket service =================")      

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'chat.message',  # must match method name 'chat_message' in consumer
            'message': json.dumps(payload)
        }
    )

    # async_to_sync(channel_layer.group_send)(
    #     group_name,
    #     {
    #         'type': 'chat_message',  # must match method name 'chat_message' in consumer
    #         'message': json.dumps(payload)
    #     }
    # )
    


