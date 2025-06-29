from facebook.utils import send_message
# from chatgpt.api import generate_chatgpt_response

def handle_message(event):
    sender_id = event['sender']['id']
    message_text = event['message'].get('text')
    
    if message_text:
        pass
        # Get response from ChatGPT
        # response_text = generate_chatgpt_response(message_text)
        
        # Send response back to Facebook
        # send_message(sender_id, response_text)