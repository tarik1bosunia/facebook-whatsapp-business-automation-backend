#!/usr/bin/env python
import os
import asyncio
import django
from django.contrib.auth import get_user_model

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'facebook_business_automation.settings')
django.setup()

async def test_llm_service():
    # Get or create a test user
    User = get_user_model()
    
    try:
        user = await User.objects.aget(email='tt@t.com')
    except User.DoesNotExist:
        user = User(email='tt@t.com', is_active=True)
        await user.asave()
    
    # Import the service after Django setup
    from llm_integration.services.llm_service import LLMService
    
    # Initialize the service
    llm_service = LLMService(user=user)
    
    # Test messages covering different scenarios
    test_cases = [
        ("What time do you open on weekdays?", "hours query"),
        ("Do you have wireless earbuds in stock?", "product query"),
        ("How can I return a defective product?", "FAQ query"),
        ("Can I schedule an oil change for Friday?", "service query"),
        ("Tell me about your company", "general query"),
        ("What's the weather today?", "unrelated query")
    ]
    
    for message, description in test_cases:
        print(f"\n{'='*50}")
        print(f"TEST CASE: {description}")
        print(f"{'-'*50}")
        print(f"USER INPUT: {message}")
        
        try:
            response = await llm_service.generate_response_async(message)
            
            print("\nRESPONSE:")
            print(response['response'])
            
            print("\nCONTEXT USED:")
            for key, value in response['context_used'].items():
                print(f"{key}: {value}")
            
            # Uncomment to see the full prompt for debugging
            # print("\nFULL PROMPT:")
            # print(response['prompt'])
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
    
    print("\nTesting complete!")

if __name__ == '__main__':
    asyncio.run(test_llm_service())


"""
==================================================
TEST CASE: hours query
--------------------------------------------------
USER INPUT: What time do you open on weekdays?

RESPONSE:
We are open from 9:00 AM to 6:00 PM Monday through Friday.

CONTEXT USED:
faqs_used: 0
products_used: 0
services_used: 0
hours_used: 1

"""
# 1. Interactive Testing Mode
# Add this function to your test file for an interactive session:
"""
async def interactive_test():
    User = get_user_model()
    user = await User.objects.aget(email='t@t.com')
    llm_service = LLMService(user=user)
    
    print("Interactive LLM Service Testing")
    print("Type 'quit' to exit\n")
    
    while True:
        message = input("You: ")
        if message.lower() in ['quit', 'exit']:
            break
            
        response = await llm_service.generate_response_async(message)
        print("\nAI:", response['response'])
        print("Context used:", response['context_used'])
        print()

"""