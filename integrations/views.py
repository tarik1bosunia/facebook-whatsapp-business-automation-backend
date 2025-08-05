from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import os
from .serializers import FacebookAuthSerializer
from business.models.integrations import FacebookIntegration
from django.contrib.auth import get_user_model
from account.permissions import IsAuthenticatedAndVerified # Import the permission class
from utils.renderers import CustomRenderer
User = get_user_model()


class FacebookAuthView(APIView):
    """
    {
        "access_token": "YOUR_SHORT_LIVED_USER_ACCESS_TOKEN",
        "app_id": "YOUR_FACEBOOK_APP_ID",
        "app_secret": "YOUR_FACEBOOK_APP_SECRET"
    }
    """
    permission_classes = [IsAuthenticatedAndVerified] # Apply the permission class
    renderer_classes = [CustomRenderer]

    def post(self, request):
        serializer = FacebookAuthSerializer(data=request.data)
        if serializer.is_valid():
            short_lived_token = serializer.validated_data['access_token']
            user = request.user # User is guaranteed to be authenticated and verified by permission_classes

            APP_ID = serializer.validated_data.get('app_id', os.environ.get('FACEBOOK_APP_ID'))
            APP_SECRET = serializer.validated_data.get('app_secret', os.environ.get('FACEBOOK_APP_SECRET'))


            # Exchange short-lived token for long-lived user access token
            GRAPH_API_VERSION = os.environ.get('FACEBOOK_GRAPH_API_VERSION', 'v23.0') # Default to v20.0 if not set
            exchange_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/oauth/access_token?grant_type=fb_exchange_token&client_id={APP_ID}&client_secret={APP_SECRET}&fb_exchange_token={short_lived_token}"
            
            
            print(f"DEBUG: Using FACEBOOK_APP_ID: {APP_ID}")
            print(f"DEBUG: Using FACEBOOK_APP_SECRET: {APP_SECRET}")
            print(f"DEBUG: FACEBOOK_GRAPH_API_VERSION: {GRAPH_API_VERSION}")
            try:
                exchange_response = requests.get(exchange_url)
                exchange_response.raise_for_status()
                long_lived_user_token_data = exchange_response.json()
                long_lived_user_token = long_lived_user_token_data.get('access_token')

                if not long_lived_user_token:
                    return Response({"error": "Could not obtain long-lived user token."}, status=status.HTTP_400_BAD_REQUEST)

                # Get long-lived page access token
                pages_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/me/accounts?access_token={long_lived_user_token}"
                pages_response = requests.get(pages_url)
                pages_response.raise_for_status()
                pages_data = pages_response.json()

                page_access_token = None
                page_id = None
                # Assuming you want the first page's access token, or you can add logic to select a specific page
                if pages_data and 'data' in pages_data and len(pages_data['data']) > 0:
                    page_access_token = pages_data['data'][0].get('access_token')
                    page_id = pages_data['data'][0].get('id')

                if not page_access_token:
                    return Response({"error": "Could not obtain page access token."}, status=status.HTTP_400_BAD_REQUEST)

                # Save the page access token to FacebookIntegration model
                facebook_integration, created = FacebookIntegration.objects.get_or_create(user=user)
                facebook_integration.access_token = page_access_token
                facebook_integration.platform_id = page_id
                facebook_integration.is_connected = True
                facebook_integration.save()

                return Response({"message": "Facebook integration successful."}, status=status.HTTP_200_OK)

            except requests.exceptions.RequestException as e:
                return Response({"error": f"Facebook API error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({"error": f"An unexpected error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)