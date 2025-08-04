from django.urls import path
from .views import FacebookAuthView

urlpatterns = [
    path('facebook-auth/', FacebookAuthView.as_view(), name='facebook-auth'),
]