from django.urls import path
from .views import FacebookAuthView

urlpatterns = [
    path('set-facebook-long-lived-page-access-token/', FacebookAuthView.as_view(), name='set-facebook-page-access-token'),
]