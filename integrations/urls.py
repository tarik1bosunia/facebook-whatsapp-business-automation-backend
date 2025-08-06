from django.urls import path
from .views import FacebookAppConfigView, FacebookAccessTokenView, FacebookVerifyTokenView, FacebookIntegrationStatusView

urlpatterns = [
    path('set-facebook-app-config/', FacebookAppConfigView.as_view(), name='set-facebook-app-config'),
    path('set-facebook-access-token/', FacebookAccessTokenView.as_view(), name='set-facebook-access-token'),
    path('set-facebook-verify-token/', FacebookVerifyTokenView.as_view(), name='set-facebook-verify-token'),
    path('facebook-integration-status/', FacebookIntegrationStatusView.as_view(), name='facebook-integration-status'),
]