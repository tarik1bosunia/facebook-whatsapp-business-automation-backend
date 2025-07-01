from rest_framework import serializers

from django.contrib.auth import get_user_model

from account.utils import Util
User = get_user_model()


# class UserChangeEmailSerializer(serializers.Serializer):
#     # TODO: here is an logical issue. user email setting without verify the email
#     password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
#     email = serializers.EmailField(max_length=255)

#     def validate(self, attrs):
#         user = self.context['request'].user
#         password = attrs['password']

#         if not user.check_password(password):
#             raise serializers.ValidationError({'password': 'Incorrect password'})
        
#         new_email = attrs['email']

#         if new_email == user.email:
#             raise serializers.ValidationError({'email': 'New email must be different from the current one'})
        
#         if User.objects.filter(email=new_email).exists():
#             raise serializers.ValidationError({'email': 'This email is already in use'})
        
#         return attrs

#     def save(self):
#         user = self.context['request'].user
#         new_email = self.validated_data['email']
#         # Instead of changing email directly:
#         # 1. Generate verification token
#         # 2. Send verification email
#         # 3. Store pending email change in database
#         # 4. Return response indicating verification needed
#         user.email = new_email
#         user.save()
#         return user
    


import logging
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from account.models import PendingEmailChange


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