from google import genai
from google.genai import types
from django.conf import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

class ChatBotUtil:
    @staticmethod
    def chat_with_gemini(prompt):
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction="You are a manager. Your name is Neko. You are replying to a customer. You are very polite and friendly. no markdown text just short reply of message",),
                contents=prompt
        )
        return response    
