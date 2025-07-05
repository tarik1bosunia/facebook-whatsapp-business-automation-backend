from .token_view import TokenObtainPairView, TokenRefreshView, VerifyUserView
from .activate_user_email_view import ActivateUserEmailView

from .user_registration_view import UserRegistrationView
from .user_logout_view import UserLogoutView
from .user_login_view import UserLoginView
from .user_delete_account_view import UserDeleteAccountView
from .user_profile_view import UserProfileView
from .change_password_view import UserChangePasswordView
from .password_reset_view import SendPasswordResetEmailView, UserPasswordResetConfirmView

from .change_email_view import UserChangeEmailView, VerifyEmailChangeView

from .check_email_existence_view import CheckEmailExistenceAPIView

from .user import UserViewSet


__all__ = [
    'TokenObtainPairView', 'TokenRefreshView', 'VerifyUserView',
    'ActivateUserEmailView',
     'UserRegistrationView', 'UserLogoutView', 'UserDeleteAccountView', 'UserLoginView', 'UserProfileView',
    'SendPasswordResetEmailView', 'UserPasswordResetConfirmView', 'UserChangePasswordView',
    'UserChangeEmailView', 'VerifyEmailChangeView', 'CheckEmailExistenceAPIView',

    "UserViewSet",

]