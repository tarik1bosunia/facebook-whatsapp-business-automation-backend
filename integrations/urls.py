from django.urls import path
from .views import FacebookAppConfigView, FacebookAccessTokenView, FacebookVerifyTokenView, FacebookIntegrationStatusView, FacebookAutoReplyStatusView, FacebookNotificationStatusView, FacebookConnectionStatusView

urlpatterns = [
    path('set-facebook-app-config/', FacebookAppConfigView.as_view(), name='set-facebook-app-config'),
    path('set-facebook-access-token/', FacebookAccessTokenView.as_view(), name='set-facebook-access-token'),
    path('set-facebook-verify-token/', FacebookVerifyTokenView.as_view(), name='set-facebook-verify-token'),
    path('facebook-integration-status/', FacebookIntegrationStatusView.as_view(), name='facebook-integration-status'),
    path('update-facebook-auto-reply-status/', FacebookAutoReplyStatusView.as_view(), name='update-facebook-auto-reply-status'),
    path('update-facebook-notification-status/', FacebookNotificationStatusView.as_view(), name='update-facebook-notification-status'),
    path('update-facebook-connection-status/', FacebookConnectionStatusView.as_view(), name='update-facebook-connection-status'),
]