from drf_yasg import openapi


compare_audio_upload_parameters=[
    openapi.Parameter(
        name='reference_file',
        in_=openapi.IN_FORM,  # Indicates this is form data
        type=openapi.TYPE_FILE,
        description='The audio file to be uploaded for feature extraction.',
        required=True,
    ),
    openapi.Parameter(
        name='query_file',
        in_=openapi.IN_FORM,  # Indicates this is form data
        type=openapi.TYPE_FILE,
        description='The audio file to be uploaded for feature extraction.',
        required=True,
    )


]


audio_upload_parameters = [
    openapi.Parameter(
        name='file',
        in_=openapi.IN_FORM,  # Indicates this is form data
        type=openapi.TYPE_FILE,
        description='The audio file to be uploaded for feature extraction.',
        required=True,
    )
]

# Define your responses in this file
audio_upload_responses = {
    200: openapi.Response(
        description="Successful feature extraction.",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'features': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description='Extracted audio features',
                ),
            },
        ),
    ),
    400: openapi.Response(
        description="Bad request.",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Error message detailing the issue.',
                ),
            },
        ),
    ),
}