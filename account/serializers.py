from rest_framework import serializers
from datetime import datetime
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, smart_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from account.utils import Util
from .models import PendingEmailChange, User
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from django.utils.crypto import get_random_string
from datetime import timedelta

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class EmailCheckSerializer(serializers.Serializer):
    email = serializers.EmailField()


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'role']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 8,  # Enforce minimum length
            }
        }

    def validate_password(self, value):
        validate_password(value)
        return value
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ['email', 'password']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError('Both email and password are required.')
        
        return attrs    


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role']
        read_only_fields = ['id', 'email'] 
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
        }



class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    new_password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)


    def validate(self, attrs):
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        user = self.context.get('user')

        # Check if new password is different
        if old_password == new_password:
            raise serializers.ValidationError({
                'new_password': 'New password must be different from old password.'
            })

        # Validate old password
        if not user.check_password(old_password):
            raise serializers.ValidationError({
                'old_password': 'Old password is incorrect.'
            })
            
        return attrs
    
    def save(self, **kwargs):
        user = self.context['user']
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()


class UserChangeEmailSerializer(serializers.Serializer):
    # TODO: here is an logical issue. user email setting without verify the email
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    email = serializers.EmailField(max_length=255)

    def validate(self, attrs):
        user = self.context['request'].user
        password = attrs['password']

        if not user.check_password(password):
            raise serializers.ValidationError({'password': 'Incorrect password'})
        
        new_email = attrs['email']

        if new_email == user.email:
            raise serializers.ValidationError({'email': 'New email must be different from the current one'})
        
        if User.objects.filter(email=new_email).exists():
            raise serializers.ValidationError({'email': 'This email is already in use'})
        
        return attrs

    def save(self):
        user = self.context['request'].user
        new_email = self.validated_data['email']
        # Instead of changing email directly:
        # 1. Generate verification token
        # 2. Send verification email
        # 3. Store pending email change in database
        # 4. Return response indicating verification needed
        user.email = new_email
        user.save()
        return user
    

class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    
    def validate_email(self, value):
        """Validate email format and existence without leaking information"""
        try:
            # Perform case-insensitive matching
            self.user = User.objects.get(email__iexact=value)
        except User.DoesNotExist:
            # Don't reveal whether email exists in the system
            pass
        return value



# class SendPasswordResetEmailSerializer(serializers.Serializer):
#     email = serializers.EmailField(max_length=255)

#     class Meta:
#         fields = ['email']

#     def validate(self, attrs):
#         email = attrs['email']

#         if User.objects.filter(email=email).exists():
#             user = User.objects.get(email=email)
#             uid = urlsafe_base64_encode(force_bytes(user.id))
#             token = PasswordResetTokenGenerator().make_token(user)
#             request = self.context['request']
#             frontend_base_url = Util.get_frontend_base_url(request)
#             link = f"{frontend_base_url}/activate/{uid}/{token}/"

#             body = f'Click following link to reset your password:\n{link}'
#             data = {
#                 'subject': 'Reset Your Password',
#                 'body': body,
#                 'to_email': user.email
#             }
#             Util.send_email(data)
#             return attrs
#         else:
#             raise serializers.ValidationError('You are not a registered user.')



class UserPasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=255,
        style={'input_type': 'password'},
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(
        max_length=255,
        style={'input_type': 'password'},
        write_only=True,
        required=True
    )

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        
        # Validate password match
        if password != confirm_password:
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match.'
            })

        # Get context data
        uid = self.context.get('uid')
        token = self.context.get('token')
        
        if not uid or not token:
            raise serializers.ValidationError({
                'token': 'Missing reset token in request.'
            })

        try:
            # Decode user ID safely
            user_id = smart_str(urlsafe_base64_decode(uid))
            self.user = User.objects.get(id=user_id, is_email_verified=True)
        except (TypeError, ValueError, OverflowError, DjangoUnicodeDecodeError, User.DoesNotExist):
            raise serializers.ValidationError({
                'token': 'Invalid or expired reset link.'
            })

        # Validate token and check if password was changed after token generation
        token_generator = PasswordResetTokenGenerator()
        
        # Check if token is still valid
        if not token_generator.check_token(self.user, token):
            raise serializers.ValidationError({
                'token': 'Invalid or expired reset link.'
            })
            
        # Check if password was changed after token was generated
        if self.user.last_password_change:
            token_created_at = token_generator.get_token_timestamp(self.user, token)
            if token_created_at < self.user.last_password_change.timestamp():
                raise serializers.ValidationError({
                    'token': 'This reset link has already been used.'
                })

        return attrs

    def save(self, **kwargs):
        password = self.validated_data['password']
        self.user.set_password(password)
        
        # Update password change timestamp
        self.user.last_password_change = timezone.now()
        self.user.save(update_fields=['password', 'last_password_change'])


class UserDeleteAccountSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    def validate(self, attrs):
        email = attrs['email']
        password = attrs['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'email': 'User with this email does not exist'})
        
        if not user.check_password(password):
            raise serializers.ValidationError({'password': 'Incorrect password'})
        
        attrs['user'] = user
        return attrs
    

import logging
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from .models import PendingEmailChange


logger = logging.getLogger(__name__)

class UserChangeEmailSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=255,
        style={'input_type': 'password'},
        write_only=True,
        trim_whitespace=False
    )
    email = serializers.EmailField(max_length=255)

    def validate(self, attrs):
        user = self.context['request'].user
        password = attrs.get('password')
        new_email = attrs.get('email', '').lower().strip()  # Normalize email

        # Check password
        if not user.check_password(password):
            raise serializers.ValidationError({"password": "Incorrect password."})

        # Skip if email isn't changing
        if user.email.lower() == new_email:
            raise serializers.ValidationError({"email": "New email cannot be the same as current email."})

        User = get_user_model()
        
        # Check if email exists in verified accounts
        if User.objects.filter(email__iexact=new_email, is_email_verified=True).exists():
            raise serializers.ValidationError({"email": "This email is already in use."})

        # Check if another user has a pending change for this email
        if PendingEmailChange.objects.filter(new_email__iexact=new_email).exclude(user=user).exists():
            raise serializers.ValidationError({
                "email": "This email address is currently being verified by another user."
            })

        return attrs

    def save(self):
        user = self.context['request'].user
        new_email = self.validated_data['email'].lower().strip()

        try:
            # Use atomic transaction for data consistency
            with transaction.atomic():
                # Delete any existing pending changes for this user
                PendingEmailChange.objects.filter(user=user).delete()
                
                # Clean up any unverified users with this email
                self._cleanup_unverified_users(new_email)
                
                # Create new pending change
                pending_change = PendingEmailChange.create_for_user(
                    user=user,
                    new_email=new_email,
                    expiration_hours=24
                )

            # Send verification email
            self._send_verification_email(user, pending_change)
            
            return pending_change

        except ValidationError as e:
            logger.error(f"Validation error in pending email change: {str(e)}")
            raise serializers.ValidationError({"email": e.message_dict.get('new_email', [])})
        
        except IntegrityError as e:
            logger.error(f"Database integrity error: {str(e)}")
            raise serializers.ValidationError({
                "error": "Could not process your request due to a database conflict. Please try again."
            })
            
        except Exception as e:
            logger.exception("Failed to process email change request")
            raise serializers.ValidationError({
                "error": "Could not process your email change request. Please try again."
            })

    def _cleanup_unverified_users(self, email):
        """Delete unverified users with this email if they exist"""
        User = get_user_model()
        # Delete unverified users with this email
        unverified_users = User.objects.filter(
            email__iexact=email, 
            is_email_verified=False
        )
        
        if unverified_users.exists():
            logger.info(f"Cleaning up {unverified_users.count()} unverified user(s) for email: {email}")
            unverified_users.delete()

    def _send_verification_email(self, user, pending_change):
        """Send verification email"""
        try:
            token = get_random_string(64)
            pending_change.token = token
            pending_change.save()
            request = self.context['request']
            frontend_base_url = Util.get_frontend_base_url(request)
            verification_url = f"{frontend_base_url}/verify-email-change/{token}/"
            
            subject = "Verify Your Email Change"
            message = (
                f"Hello {user.get_full_name()},\n\n"
                f"Please click the link below to verify your new email address:\n\n"
                f"{verification_url}\n\n"
                f"This link will expire in 24 hours.\n"
                f"If you didn't request this change, please contact support immediately."
            )
            data = {
                'subject': subject,
                'body': message,
                'to_email': pending_change.new_email
            }

            Util.send_email(data=data)
            
            logger.info(f"Verification email sent to {pending_change.new_email}")
            
        except Exception as e:
            logger.exception("Failed to send verification email")



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['full_name'] = user.get_full_name()
        return token
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'role']