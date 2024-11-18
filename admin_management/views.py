from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.models import CustomUser
from authentication.serializers import CustomUserSerializer
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema

User = get_user_model()


class CreateAdminUserView(APIView):
    @swagger_auto_schema(
    operation_description="Update user details",
    request_body=CustomUserSerializer,
    )
    def post(self, request):

        data = request.data
        data['role'] = 'Admin'
        data['is_verified'] = True  
        serializer = CustomUserSerializer(data=data)    
        if serializer.is_valid():
            # Save the user as an admin
            serializer.save()
            return Response({
                'success':True,
                'message':'Admin user created successfully',
                'data':serializer.data
            },status=status.HTTP_201_CREATED )
        
        return Response(
            {'success':False,
             'error':serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
