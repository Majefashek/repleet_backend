from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import MyReferenceTracks
from .serializers import ReferenceTracksSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework import status
from django.core.files.storage import default_storage
from .models import MyReferenceTracks, AudioTrack
from .serializers import ReferenceTracksSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .swagger_schemas import audio_upload_parameters
from rest_framework.parsers import MultiPartParser
class UploadReferenceTrackView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_description="Uploads an audio file as a reference track and saves it with specified category and difficulty.",
        manual_parameters=audio_upload_parameters,
    )
    def post(self, request):
        audio_file = request.data.get('audio_file')  # Assuming the field name is 'audio'
        name = request.data.get('name')
        artist = request.data.get('artist')
        description = request.data.get('description')
        category = request.data.get('category')
        difficulty_level = request.data.get('difficulty_level')
        genre = request.data.get('genre')
        musical_element = request.data.get('musical_element')
        music_length = request.data.get('music_length')
        

        try:
            # Check for required fields
            if not audio_file or not category or not difficulty_level or not genre or not musical_element or not music_length:
                return Response(
                    {"error": "All fields (audio, category, difficulty_level, genre, musical_element, music_length) are required.",
                     "data":name},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Save the audio file
            file_path = default_storage.save(audio_file.name, audio_file)

            # Create the ReferenceTracks instance
            audio_track = AudioTrack(
                audio_file=file_path,
                name=name,
                artist=artist,
                description=description,
                category=category,
                difficulty_level=difficulty_level,
                genre=genre,
                musical_element=musical_element,
                music_length=music_length
            )
            audio_track.save()


            reference_tracks = MyReferenceTracks(
                audio=audio_track,
                uploaded_by=request.user  
            )
            reference_tracks.save()

            return Response(
                {'success': True, 'message': "Reference track uploaded successfully.", "track_id": reference_tracks.id},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            raise e
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class ReferenceTracksByDifficultyView(APIView): 
    serializer_class = ReferenceTracksSerializer

    @swagger_auto_schema(
        operation_description="Get reference tracks filtered by difficulty level",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'difficulty': openapi.Schema(type=openapi.TYPE_STRING, description="Difficulty level to filter by"),
            },
        ),
        responses={200: openapi.Response('Success', ReferenceTracksSerializer(many=True))},
    )
    def post(self, request, *args, **kwargs):  
        difficulty = request.data.get('difficulty', None)  
        queryset = self.get_queryset(difficulty)

        serializer = self.serializer_class(queryset, many=True) 
        return Response({'success': True, 'data': serializer.data})

    def get_queryset(self, difficulty): 
        if difficulty:
            return MyReferenceTracks.objects.filter(audio__difficulty_level=difficulty)
        return MyReferenceTracks.objects.all()
    


class DeleteReferenceTrackView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    @swagger_auto_schema(
        operation_description="Delete a reference track by ID",
        responses={
            200: openapi.Response('Deleted successfully.', ReferenceTracksSerializer),  # Corrected response
            404: openapi.Response('Reference track not found.', ReferenceTracksSerializer),  # Corrected response
        },
    )
    def delete(self, request, track_id, *args, **kwargs):
        try:
            # Attempt to retrieve the reference track by ID
            reference_track = MyReferenceTracks.objects.get(id=track_id)
            reference_track.delete()  # Delete the reference track
            return Response({'success': True, 'message': 'Deleted successfully.'}, status=status.HTTP_200_OK)  # Return success message
        except MyReferenceTracks.DoesNotExist:
            return Response({'success': False, 'error': 'Reference track not found.'}, status=status.HTTP_404_NOT_FOUND)  # Handle not found