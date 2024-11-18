from rest_framework import status
from drf_yasg import openapi
from .serializers import SignUpSerializer

responses={
        status.HTTP_200_OK: openapi.Response(
            description="User details updated successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Operation success status"),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description="Success message"),
                    'data': SignUpSerializer
                }
            )
        ),
        status.HTTP_400_BAD_REQUEST: openapi.Response(description="Bad request"),
        status.HTTP_401_UNAUTHORIZED: openapi.Response(description="Authentication credentials were not provided")
    }

image_upload_parameters = [
    openapi.Parameter(
        name='profile_image',
        in_=openapi.IN_FORM,  # Indicates this is form data
        type=openapi.TYPE_FILE,
        description='Profile image to be uploaded.',
        required=True,
    )
]