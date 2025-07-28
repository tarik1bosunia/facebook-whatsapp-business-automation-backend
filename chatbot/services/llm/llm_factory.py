from django.conf import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

class LLMFactory:
    """Factory for creating different types of LLMs"""
    
    @staticmethod
    def create_llm(model_code: str, api_key: str = None, **kwargs):
        """Factory method for creating LLM instances"""
        model_code = model_code.lower()
        
        if 'gemini' in model_code:
            return LLMFactory._create_gemini(model_code, api_key, **kwargs)
        elif model_code.startswith('gpt-'):
            return LLMFactory._create_openai(model_code, api_key, **kwargs)
        else:
            return LLMFactory._create_custom(model_code, api_key, **kwargs)

    @staticmethod
    def _create_gemini(model_code: str, api_key: str, **kwargs):
        """Create Google Gemini instance"""
        api_key = api_key or settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("Gemini API key required")

        return ChatGoogleGenerativeAI(
            model=model_code,
            google_api_key=api_key,
            temperature=0.7,
            max_output_tokens=2000,
            **kwargs
        )

    @staticmethod
    def _create_openai(model_code: str, api_key: str, **kwargs):
        """Create OpenAI instance"""
        api_key = api_key or settings.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OpenAI API key required")

        return ChatOpenAI(
            model=model_code,
            openai_api_key=api_key,
            temperature=0.7,
            max_tokens=2000,
            model_kwargs={
                'top_p': 0.9,
                'frequency_penalty': 0.1
            },
            **kwargs
        )

    @staticmethod
    def _create_custom(model_code: str, api_key: str, **kwargs):
        """Create custom LLM instance"""
        endpoint = getattr(settings, 'CUSTOM_LLM_ENDPOINT', None)
        if not endpoint:
            raise ValueError("Custom LLM endpoint not configured")

        return ChatOpenAI(
            base_url=endpoint,
            api_key=api_key,
            temperature=0.7,
            max_tokens=2000,
            **kwargs
        )
