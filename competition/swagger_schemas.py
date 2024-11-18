from drf_yasg import openapi
 
audio_upload_parameters = [
    openapi.Parameter(
        'competition_id',
        openapi.IN_FORM,
        description="ID of the competition",
        type=openapi.TYPE_INTEGER,
        required=True,
    ),
    openapi.Parameter(
        'name',
        openapi.IN_FORM,
        description="Name of the audio track",
        type=openapi.TYPE_STRING,
        required=True,
    ),
    openapi.Parameter(
        'description',
        openapi.IN_FORM,
        description="Description of the audio track",
        type=openapi.TYPE_STRING,
        required=True,
    ),
    openapi.Parameter(
        'artist',
        openapi.IN_FORM,
        description="Artist of the audio track",
        type=openapi.TYPE_STRING,
        required=True,
    ),
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
    openapi.Parameter(
        'genre',  # New field for genre
        openapi.IN_FORM,
        description="Genre of the music (Pop, Rock, Classical, Jazz, Blues, Hip-Hop/Rap, R&B, Country, Reggae, Soul, Metal, Gospel)",
        type=openapi.TYPE_STRING,
        enum=['Pop', 'Rock', 'Classical', 'Jazz', 'Blues', 'Hip-Hop/Rap', 'R&B', 'Country', 'Reggae', 'Soul', 'Metal', 'Gospel'],
        required=True,
    ),
    openapi.Parameter(
        'musical_element',  # New field for musical elements
        openapi.IN_FORM,
        description="Musical elements (Chord Progression, Solo Runs, Chord P & Solo Runs)",
        type=openapi.TYPE_STRING,
        enum=['Chord Progression', 'Solo Runs', 'Chord P & Solo Runs'],
        required=True,
    ),
    openapi.Parameter(
        'music_length',  # New field for music length
        openapi.IN_FORM,
        description="Length of the music (Part of Music, Full Music)",
        type=openapi.TYPE_STRING,
        enum=['Part of Music', 'Full Music'],
        required=True,
    ),
]


add_existing_competition_audio_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'competition_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the competition to which the audio will be added."),
        'audio_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the existing audio track to be associated with the competition."),
    },
    required=['competition_id', 'audio_id'] 
)    
add_existing_competition_audio_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'message': openapi.Schema(type=openapi.TYPE_STRING),
        'error': openapi.Schema(type=openapi.TYPE_STRING),
    }
)