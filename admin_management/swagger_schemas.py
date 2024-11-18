from drf_yasg import openapi



reference_parameters=[
            openapi.Parameter(
                'category',
                openapi.IN_QUERY,
                description="Category of the audio (Piano, Guitar, Drum, Vocals)",
                type=openapi.TYPE_STRING,
                enum=['Piano', 'Guitar', 'Drum', 'Vocals'],
                required=False,
            ),
            openapi.Parameter(
                'difficulty',
                openapi.IN_QUERY,
                description="Difficulty level of the audio (Easy, Medium, Hard)",
                type=openapi.TYPE_STRING,
                enum=['Easy', 'Medium', 'Hard'],
                required=False,
            ),
        ],


audio_upload_parameters = [
    openapi.Parameter(
        'audio_file',
        openapi.IN_FORM,
        description="The audio file to upload (reference track)",
        type=openapi.TYPE_FILE,
        required=True,
    ),
    openapi.Parameter(
        'category',
        openapi.IN_FORM,
        description="Category of the audio (Piano, Guitar, Drum, Vocals)",
        type=openapi.TYPE_STRING,
        enum=['Piano', 'Guitar', 'Drum', 'Vocals'],
        required=True,
    ),
    openapi.Parameter(
        'difficulty_level',
        openapi.IN_FORM,
        description="Difficulty level of the audio (Easy, Medium, Hard)",
        type=openapi.TYPE_STRING,
        enum=['Easy', 'Medium', 'Hard'],
        required=True,
    ),
]