from django.urls import path
from .views import FacebookAppConfigView, FacebookAccessTokenView, FacebookVerifyTokenView

urlpatterns = [
    path('set-facebook-app-config/', FacebookAppConfigView.as_view(), name='set-facebook-app-config'),
    path('set-facebook-access-token/', FacebookAccessTokenView.as_view(), name='set-facebook-access-token'),
    path('set-facebook-verify-token/', FacebookVerifyTokenView.as_view(), name='set-facebook-verify-token'),
]