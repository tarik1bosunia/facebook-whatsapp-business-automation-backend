from django.urls import path, include

from . import views
from .views.rbac import BusinessmanOnlyView,  SuperAdminOnlyView

# TODO: sepharate every view and serializers in sepharate file

from rest_framework.routers import DefaultRouter

router = DefaultRouter()


router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    # just test
    path('superadmin/', SuperAdminOnlyView.as_view()),
    path('businessman/', BusinessmanOnlyView.as_view()),

    # superadmin
    path('', include(router.urls)),


    # auth
    path('auth/logout/', views.UserLogoutView.as_view(), name='logout'),
    path('auth/delete-account/',
         views.UserDeleteAccountView.as_view(), name='delete-account'),
    path('auth/change-email/',
         views.UserChangeEmailView.as_view(), name='change-email'),
    path('auth/change-password/',
         views.UserChangePasswordView.as_view(), name='change-password'),
    path('auth/profile/', views.UserProfileView.as_view(),
         name='profile'),  # both get and update profile


    # without authentication needed
    path('check-email/', views.CheckEmailExistenceAPIView.as_view(),
         name='check-email'),
    path('registration/', views.UserRegistrationView.as_view(), name='registration'),
    path('activate/<str:uid>/<str:token>/',
         views.ActivateUserEmailView.as_view(), name="activate user email"),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('verify-email-change/<str:token>/',
         views.VerifyEmailChangeView.as_view(), name='verify-email-change',),
    path('send-password-reset-email/', views.SendPasswordResetEmailView.as_view(),
         name='send-password-reset-email'),
    path('password-reset-confirm/<str:uid>/<str:token>/',
         views.UserPasswordResetConfirmView.as_view(), name='password-reset-confirm'),


    path('token/verify/', views.VerifyUserView.as_view(), name="token_verify"),
    path('token/', views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', views.TokenRefreshView.as_view(), name='token_refresh'),
]
