# services/llm/agents.py
from langchain.agents import AgentType, initialize_agent

from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from django.conf import settings

from langchain_google_genai  import ChatGoogleGenerativeAI

from messaging.models.chatmessage import ChatMessage

GEMINI_API_KEY = settings.GEMINI_API_KEY

class ChatAgent:
    def __init__(self, user, conversation=None):
        self.user = user
        self.conversation = conversation
        print("====================== from ChatAgent ====================")
        print("user", self.user)

        self.llm = ChatGoogleGenerativeAI(
            google_api_key=GEMINI_API_KEY,
            model="gemini-2.0-flash",
            temperature=0.7,
        )
        
        # self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.memory = self._setup_memory()
        self.tools = self._setup_tools()
        self.agent = self._create_agent()


    def _setup_memory(self):
        """Initialize memory with previous messages if conversation exists"""
        memory = ConversationBufferMemory(memory_key="chat_history")
        
        if self.conversation:
            # Load previous messages in correct order (oldest first)
            previous_messages = ChatMessage.objects.filter(
                conversation=self.conversation
            ).order_by('created_at')
            
            for msg in previous_messages:
                if msg.sender == 'customer':
                    memory.chat_memory.add_user_message(msg.message)
                else:  # AI or business messages
                    memory.chat_memory.add_ai_message(msg.message)
                    
        return memory     

    def _setup_tools(self):
        return [
            Tool(
                name="Product Search",
                func=self._get_products_info,
                description="Useful for answering questions about products, pricing, and availability"
            ),
            Tool(
                name="FAQ Search",
                func=self._get_faq_info,
                description="Useful for answering frequently asked questions"
            ),
            Tool(
                name="Business Info",
                func=self._get_business_info,
                description="Useful for answering questions about the business, contact info, or services"
            )
        ]
    


    def _create_agent(self):
        return initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            max_iterations=3,
            handle_parsing_errors=True,
        )
    


    def _get_products_info(self, query):
        from django.template.loader import render_to_string
        from business.models import Product
        
        products = Product.objects.filter(
            user=self.user,
            # name__icontains=query
        )[:5]  # Limit to 5 most relevant

        
        return render_to_string('llm/product_details.txt', {'products': products})

    def _get_faq_info(self, query):
        from knowledge_base.models import FAQ
        
        faqs = FAQ.objects.filter(
            category__user=self.user,
            # question__icontains=query
        )[:3]
        
        return "\n".join([f"Q: {f.question}\nA: {f.answer}" for f in faqs])

    def _get_business_info(self, query):
        from business.models import BusinessProfile
        
        business = BusinessProfile.objects.get(user=self.user)
        return (
            f"Business Name: {business.name}\n"
            f"Description: {business.description}\n"
            f"Contact: {business.email} | {business.phone}\n"
            f"Website: {business.website}"
        )

    def get_response(self, message):
        return self.agent.run(input=message)