from email.utils import formataddr
from typing import Dict, Optional
from django.contrib.auth import authenticate
from django.core.mail import EmailMessage
import os

from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from account.enums import AuthProvider
from account.models import User

from urllib.parse import urlparse
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AnonymousUser


class Util:

    @staticmethod
    def send_email(data: Dict[str, str])-> bool:
        """
        Send an email with the provided data.
        
        Args:
            data: Dictionary containing email parameters with keys:
                - subject: Email subject
                - body: Email body content
                - to_email: Recipient email address(es)
                - from_email: Optional sender email
                - reply_to: Optional reply-to address
                - cc: Optional CC addresses
                - bcc: Optional BCC addresses
                - html_body: Optional HTML content
        
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Validate required fields
            if not all(key in data for key in ['subject', 'body', 'to_email']):
                raise ValueError("Missing required email fields")
            

            # Prepare email parameters
            to_emails = [data['to_email']] if isinstance(data['to_email'], str) else data['to_email']
            from_email = data.get('from_email') or os.environ.get('EMAIL_FROM') or settings.DEFAULT_FROM_EMAIL
            reply_to = data.get('reply_to')
            cc = data.get('cc', [])
            bcc = data.get('bcc', [])
            html_body = data.get('html_body')

            # Create email message
            email = EmailMessage(
                subject=data['subject'],
                body=data['body'],
                from_email=formataddr(('', from_email)),  # Proper email formatting
                to=to_emails,
                cc=cc,
                bcc=bcc,
                reply_to=[reply_to] if reply_to else None
            )

             # Add HTML alternative if provided
            if html_body:
                email.content_subtype = "html"
                email.alternatives = [(html_body, 'text/html')]

            # Send email
            sent_count = email.send(fail_silently=False)
            return sent_count > 0

            

        except Exception as e:
            # Log the error (consider using logging framework in production)
            print(f"Failed to send email: {str(e)}")
            return False

    @classmethod
    def send_template_email(
        cls,
        template_name: str,
        context: Dict[str, str],
        to_email: str,
        subject: str,
        from_email: Optional[str] = None,
        **kwargs
    ) -> bool:
        """
        Send an email using a template (example implementation).
        
        Args:
            template_name: Name of the template to use
            context: Dictionary with template variables
            to_email: Recipient email address
            subject: Email subject
            from_email: Optional sender email
            **kwargs: Additional email parameters
        
        Returns:
            bool: True if email was sent successfully
        """
        # In a real implementation, you would render the template here
        body = f"Template: {template_name}\nContext: {context}"
        
        email_data = {
            'subject': subject,
            'body': body,
            'to_email': to_email,
            'from_email': from_email,
            **kwargs
        }
        
        return cls.send_email(email_data)        

    @staticmethod
    def get_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    @staticmethod
    def login_user(email, password):
        user = authenticate(email=email, password=password)

        if user is not None:
            token = Util.get_tokens_for_user(user)
            return Response({'token': token, 'message': 'Login Success'}, status=status.HTTP_200_OK)
        else:
            print('Email or Password is not Valid')
            return Response({'errors': {'non_field_errors': ['Email or Password is not Valid']}},
                            status=status.HTTP_404_NOT_FOUND)
        
    @staticmethod
    def get_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        } 

    @staticmethod
    def _validate_frontend_url(url):
        """Validate that the URL belongs to allowed frontend domains."""
        domain = urlparse(url).netloc
        if not any(domain == allowed or domain.endswith(f'.{allowed}') 
                for allowed in settings.ALLOWED_FRONTEND_DOMAINS):
            raise ValidationError("Frontend URL not allowed")
        return url   

    def get_frontend_base_url(request):
        """Get frontend base URL from request header or use default."""
        frontend_url = request.META.get('HTTP_X_FRONTEND_BASE_URL', settings.FRONTEND_BASE_URL)
        return Util._validate_frontend_url(frontend_url)   

    
    def is_user_verified(user: User):
        """
        Check if a user is verified based on their authentication provider.
        
        Args:
            user: The user object to check (can be None or AnonymousUser)
            
        Returns:
            bool: True if user is verified, False otherwise
        """
        if user is None or isinstance(user, AnonymousUser):
            return False
        
        if user.auth_provider == AuthProvider.EMAIL:
            return user.is_email_verified
        # All other auth providers are considered verified
        return True