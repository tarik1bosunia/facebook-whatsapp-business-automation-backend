class MessageService:
    @staticmethod
    def process_incoming(message_data, platform):
        """Standardize incoming message format"""
        standard_msg = {
            "platform": platform,
            "message_id": message_data.get('id'),
            "sender_id": message_data.get('from'),
            "content": message_data.get('text', {}).get('body') or
                      message_data.get('attachments', []),
            "timestamp": message_data.get('timestamp')
        }
        return standard_msg

    @staticmethod
    def send_message(provider, recipient, message, **kwargs):
        """Unified send message interface"""
        return provider.send(
            to=recipient,
            text=message,
            **kwargs
        )