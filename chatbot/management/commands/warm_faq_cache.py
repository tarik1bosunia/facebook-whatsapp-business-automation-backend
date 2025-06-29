# management/commands/warm_faq_cache.py
from django.core.management.base import BaseCommand
from chatbot.langchain import FAQVectorSearch

class Command(BaseCommand):
    help = 'Warms the FAQ vector cache'

    def handle(self, *args, **options):
        self.stdout.write("Initializing FAQ vector store...")
        search = FAQVectorSearch()
        search.initialize_vectorstore()
        self.stdout.write("FAQ vector store initialized successfully!")