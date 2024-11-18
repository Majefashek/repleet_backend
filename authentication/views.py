from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework import response, status
from . import serializers, models
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt

# from .utils import Util
from django.conf import settings
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .models import CustomUser
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserTokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .swagger_schemas import *
from PIL import Image
import io
from rest_framework.parsers import MultiPartParser
from .tasks import *
import random
from datetime import timedelta
from django.utils import timezone
from . import  utils
 
class GetUserByIdView(generics.RetrieveAPIView):
    #serializer_class = CustomUserSerializer  # Specify the serializer to use
    def get(self, request,**kwargs):
        try:
            user = CustomUser.objects.get(id=kwargs['user_id'])
            serializer =CustomUserSerializer(user)
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except CustomUser.DoesNotExist:
            return Response(
                {"success": False, "error": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class ProfileImageUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [
        MultiPartParser,
    ]

    @swagger_auto_schema(
        operation_description="Uploade profile image.",
        manual_parameters=image_upload_parameters,  
    )
    def post(self, request):
        if "profile_image" not in request.FILES:
            return Response(
                {"error": "No profile image provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile_image = request.FILES["profile_image"]
        try:
            img = Image.open(profile_image)
            img.verify()
        except (IOError, SyntaxError) as e:
            return Response(
                {"error": "Uploaded file is not a valid image."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        user.profile_image = profile_image
        user.save()
        return Response(
            {"message": "Profile image updated successfully."},
            status=status.HTTP_200_OK,
        )


class GetUserDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            serializer = CustomUserSerializer(user)
            return Response(
                {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


@swagger_auto_schema(
    operation_description="Update user details",
    request_body=SignUpSerializer,
    responses=responses,
)
class UpdateUserDetails(generics.UpdateAPIView):
    serializer_class = UpdateUserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return Response(
            {
                "success": True,
                "message": "User details updated successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)



class UserTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            custom_data = {"message": "Login successful", "success": True}
            custom_data.update(response.data)
            return Response(custom_data, status=status.HTTP_200_OK)
        except ValidationError as e:
            # Catch ValidationError and return the specific error messages
            return Response(
                {"success": False, "errors": e.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


class SignUp(GenericAPIView):
    serializer_class = SignUpSerializer

    def post(self, request):
        try:
            data = request.data
            email = data.get("email")
            role = data.get('role')

            # Prevent admin signup
            if role == 'Admin':
                return Response({'success': False, 'error': 'You do not have the privilege to sign up as admin'},
                                status=400)

            # Check if the user already exists in the database
            user = CustomUser.objects.filter(email=email).first()

            if not user:  # If the user does not exist, create a new user
                serializer = self.serializer_class(data=data)
                serializer.is_valid(raise_exception=True)
                user = serializer.save()
                user_verified = False  # Newly created user, not verified
            else:
                # If the user exists, check if the email is verified
                user_verified = user.is_verified  # Assuming `is_verified` is a field in your model

            # Handle the case where the user exists but isn't verified
            if user_verified:
                return Response(
                    {"success": False, "message": "The account is already verified."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                # User is not verified, send a verification email
                pin_code = f"{random.randint(100000, 999999)}"
                expiry_date = timezone.now() + timedelta(minutes=10)

                # Create or update the verification entry for the user
                UserVerification.objects.update_or_create(
                    user_id=user.id,
                    defaults={'pin_code': pin_code, 'expiry_date': expiry_date}
                )

                # Send the verification email to the user
                self.send_verification_email(request, user, pin_code)

                return Response(
                    {"success": True, "message": "Verification email sent. Please check your inbox."},
                    status=status.HTTP_200_OK
                )

        except Exception as e:
            raise e 
            return Response(
                {"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def send_verification_email(self, request, user, pin_code):
        # Your existing code to send the verification email
        verify_url = 'https://repeetfrontenddev-production.up.railway.app/'
        email_body = (
            f"Hi {user.username},\n\n"
            f"Use the pin below to verify your email:\n\n"
            f"{pin_code}\n\n"
            f"Please note that the code will expire in 10 minutes.\n\n"
            f"Click on the following link to verify: {verify_url}/{pin_code}\n"
        )

        data = {
            "email_body": email_body,
            "to_email": user.email,
            "email_subject": "Verify your email",
        }

        send_email(data=data)



# Endpoint for email verification
class VerifyEmail(GenericAPIView):
    serializer_class = EmailVerificationSerializer

    token_param_config = openapi.Parameter(
        "token",
        in_=openapi.IN_QUERY,
        description="Description",
        type=openapi.TYPE_STRING,
    )

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get("token")
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            print(payload)
            user = CustomUser.objects.get(id=payload["user_id"])
            if not user.is_verified:
                user.is_verified = True
                user.save()

            self.send_welcome_email(request,user)

            return response.Response(
                {"success": True, "email": "Successfully activated"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            self.send_welcome_email(request,user)
            return Response({'success':False,'error': str(e)},status=400)


    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        if password:
            instance.set_password(password)
            instance.save()
        return instance
    
    def send_welcome_email(self, request,user):
        email_body = (
            f"Subject: Welcome to Repeet – Your Journey to Musical Mastery Begins Here!\n\n"
            f"Hi {user.username},\n\n"
            "Welcome to Repeet! We’re thrilled to have you join a community where music meets innovation.\n\n"
            "With Repeet, you’re about to embark on an exciting journey to improve your musical skills through "
            "challenges, competitions, and self-learning activities, all while receiving personalized feedback from our cutting-edge AI. "
            "Whether you're a beginner or an advanced musician, we’re here to help you grow, one note at a time!\n\n"
            "Here’s what you can expect from Repeet:\n"
            "🎶 **Interactive Challenges**: Put your skills to the test with fun and engaging challenges designed to push your limits and unlock new levels of mastery.\n"
            "🏆 **Competitions**: Participate in friendly competitions, gain recognition, and see how you measure up with other musicians around the world.\n"
            "🤖 **AI Feedback**: Our AI listens and provides instant feedback, helping you improve with precise insights on your performance.\n"
            "🎓 **Self-Learning Tools**: Access a variety of self-learning activities that let you practice at your own pace and level up your skills on your schedule.\n\n"
            "We’re excited to see your musical journey unfold! If you have any questions or need assistance, feel free to reach out.\n\n"
            "Let’s get started—log in to your account, explore the dashboard, and dive into your first challenge. Welcome to the Repeet family!\n\n"
            "Best regards,\n"
            "The Repeet Team\n"
        )
    
    # Set up email data to send
        data = {
            "email_body": email_body,
            "to_email": user.email,
            "email_subject": "Welcome to Repeet – Your Journey to Musical Mastery Begins Here!"
        }
        
    # Send email
        send_email(data=data) 


class PasswordRequestChange(GenericAPIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email"],  # Corrected to 'email'
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,  #
                    format=openapi.FORMAT_EMAIL, 
                    description="Provide the email to get link for resetting password.",
                ),
            },
        ) 
    ) 
    def post(self, request):
        data = request.data
        email = data.get("email")
        user_exists = CustomUser.objects.filter(email=email).exists()

        if user_exists:
            user = CustomUser.objects.get(email=email)
            tokens = RefreshToken.for_user(user).access_token
            self.send_password_reset_email(request, user, tokens)
            return response.Response(
                {"success": True, "message": "Password reset link sent to your email"},
                status=status.HTTP_200_OK,
            )
        else:
            return response.Response(
                {"success": False, "error": "User does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def send_password_reset_email(self, request, user, tokens):
        current_site = get_current_site(request).domain
        relative_link = reverse("password-reset")
        absurl = f"http://{current_site}{relative_link}?token={str(tokens)}"
        email_body = (
            f"Hi {user.username}, Use the link below to reset your password \n{absurl}"
        )
        data = {
            "email_body": email_body,
            "to_email": user.email,
            "email_subject": "Reset your password",
        }
        send_email(data=data)

    def get_serializer_class(self):
        return None


class PasswordReset(GenericAPIView):
    serializer_class = PasswordResetSerializer

    token_param_config = openapi.Parameter(
        "token",
        in_=openapi.IN_QUERY,
        description="Description",
        type=openapi.TYPE_STRING,
    )

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get("token")
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            print(payload)
            user = CustomUser.objects.get(id=payload["user_id"])
            return response.Response(
                {"success": True, "message": "Token verified", "user_id": user.id},
                status=status.HTTP_200_OK,
            )
        except jwt.ExpiredSignatureError as identifier:
            return response.Response(
                {"success": False, "error": "Token Expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except jwt.exceptions.DecodeError as identifier:
            return response.Response(
                {"success": False, "error": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def post(self, request):
        token = request.GET.get("token")
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            user = CustomUser.objects.get(id=payload["user_id"])

            serializer = self.get_serializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)  
            serializer.save() 

            return response.Response(
                {"success": True, "message": "Password reset successful"},
                status=status.HTTP_200_OK,
            )
        except jwt.ExpiredSignatureError:
            return response.Response(
                {"success": False, "error": "Token Expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except jwt.exceptions.DecodeError:
            return response.Response(
                {"success": False, "error": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except CustomUser.DoesNotExist:
            return response.Response(
                {"success": False, "error": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

class VerifyPinView(APIView):
    @swagger_auto_schema(
    operation_description="Verify Pin", 
    request_body=VerifyPinSerializer,
    )
    def post(self, request):
        serializer = VerifyPinSerializer(data=request.data)
        user = CustomUser.objects.get(email=request.data.get('email'))

        if serializer.is_valid():
            user = CustomUser.objects.get(email=serializer.validated_data['email'])
            user.is_verified = True
            user.save()
            self.send_welcome_email(request,user)
            return Response({"message": "Email verification successful!"}, status=status.HTTP_200_OK)
        self.send_welcome_email(request,user)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def send_welcome_email(self, request,user):
        email_body = (
            f"Hi {user.username},\n\n"
            "Welcome to Repeet! We’re thrilled to have you join a community where music meets innovation.\n\n"
            "With Repeet, you’re about to embark on an exciting journey to improve your musical skills through "
            "challenges, competitions, and self-learning activities, all while receiving personalized feedback from our cutting-edge AI. "
            "Whether you're a beginner or an advanced musician, we’re here to help you grow, one note at a time!\n\n"
            "Here’s what you can expect from Repeet:\n"
            "🎶 **Interactive Challenges**: Put your skills to the test with fun and engaging challenges designed to push your limits and unlock new levels of mastery.\n"
            "🏆 **Competitions**: Participate in friendly competitions, gain recognition, and see how you measure up with other musicians around the world.\n"
            "🤖 **AI Feedback**: Our AI listens and provides instant feedback, helping you improve with precise insights on your performance.\n"
            "🎓 **Self-Learning Tools**: Access a variety of self-learning activities that let you practice at your own pace and level up your skills on your schedule.\n\n"
            "We’re excited to see your musical journey unfold! If you have any questions or need assistance, feel free to reach out.\n\n"
            "Let’s get started—log in to your account, explore the dashboard, and dive into your first challenge. Welcome to the Repeet family!\n\n"
            "Best regards,\n"
            "The Repeet Team\n"
        )
    
    # Set up email data to send
        data = {
            "email_body": email_body,
            "to_email": user.email,
            "email_subject": "Welcome to Repeet – Your Journey to Musical Mastery Begins Here!"
        }
        
    # Send email
        send_email(data=data) 

