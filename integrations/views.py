from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import os
from .serializers import FacebookAccessTokenSerializer, FacebookAppSerializer, FacebookVerifyTokenSerializer, FacebookIntegrationStatusSerializer
from business.models.integrations import FacebookIntegration
from django.contrib.auth import get_user_model
from account.permissions import IsAuthenticatedAndVerified
from utils.renderers import CustomRenderer
User = get_user_model()


class FacebookAppConfigView(APIView):
    """
    {
        "app_id": "YOUR_FACEBOOK_APP_ID",
        "app_secret": "YOUR_FACEBOOK_APP_SECRET"
    }
    """
    permission_classes = [IsAuthenticatedAndVerified]
    renderer_classes = [CustomRenderer]

    def post(self, request):
        serializer = FacebookAppSerializer(data=request.data)
        if serializer.is_valid():
            app_id = serializer.validated_data.get('app_id')
            app_secret = serializer.validated_data.get('app_secret')
            user = request.user

            facebook_integration, created = FacebookIntegration.objects.get_or_create(user=user)
            if app_id:
                facebook_integration.app_id = app_id
            if app_secret:
                facebook_integration.app_secret = app_secret
            facebook_integration.save()

            return Response({"message": "Facebook App ID and Secret updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FacebookAccessTokenView(APIView):
    """
    {
        "access_token": "YOUR_SHORT_LIVED_USER_ACCESS_TOKEN",
    }
    """
    permission_classes = [IsAuthenticatedAndVerified]
    renderer_classes = [CustomRenderer]

    def post(self, request):
        serializer = FacebookAccessTokenSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            short_lived_token = serializer.validated_data['access_token']
            user = request.user
            
            # Retrieve APP_ID and APP_SECRET from FacebookIntegration model
            # This logic is now handled by the serializer's validate method
            try:
                facebook_integration = FacebookIntegration.objects.get(user=user)
                APP_ID = facebook_integration.app_id
                APP_SECRET = facebook_integration.app_secret
            except FacebookIntegration.DoesNotExist:
                # This case should ideally be caught by the serializer's validation
                # but kept as a fallback
                return Response({"error": "Facebook App ID and Secret not configured. Please set them first."}, status=status.HTTP_400_BAD_REQUEST)

            # The serializer now handles the validation of APP_ID and APP_SECRET
            # if not APP_ID or not APP_SECRET:
            #     return Response({"error": "Facebook App ID and Secret are required but not set."}, status=status.HTTP_400_BAD_REQUEST)

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
                facebook_integration.access_token = page_access_token
                facebook_integration.platform_id = page_id
                facebook_integration.save()

                return Response({"message": "Facebook Access Token updated successfully."}, status=status.HTTP_200_OK)


            except requests.exceptions.RequestException as e:
                return Response({"error": f"Facebook API error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({"error": f"An unexpected error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FacebookVerifyTokenView(APIView):
    """
    {
        "verify_token": "YOUR_VERIFY_TOKEN"
    }
    """
    permission_classes = [IsAuthenticatedAndVerified]
    renderer_classes = [CustomRenderer]

    def post(self, request):
        serializer = FacebookVerifyTokenSerializer(data=request.data)
        if serializer.is_valid():
            verify_token = serializer.validated_data['verify_token']
            user = request.user

            facebook_integration, created = FacebookIntegration.objects.get_or_create(user=user)
            facebook_integration.verify_token = verify_token
            facebook_integration.save()

            return Response({"message": "Facebook Verify Token updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FacebookIntegrationStatusView(APIView):
    permission_classes = [IsAuthenticatedAndVerified]
    renderer_classes = [CustomRenderer]

    def get(self, request):
        user = request.user
        try:
            facebook_integration = FacebookIntegration.objects.get(user=user)
            app_id_set = bool(facebook_integration.app_id)
            app_secret_set = bool(facebook_integration.app_secret)
            long_live_token_set = bool(facebook_integration.access_token) # access_token is the long-lived token
            verify_token_set = bool(facebook_integration.verify_token)
        except FacebookIntegration.DoesNotExist:
            app_id_set = False
            app_secret_set = False
            long_live_token_set = False
            verify_token_set = False

        data = {
            "app_id_set": app_id_set,
            "app_secret_set": app_secret_set,
            "long_live_token_set": long_live_token_set,
            "verify_token_set": verify_token_set,
        }
        serializer = FacebookIntegrationStatusSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)