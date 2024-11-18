from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from .swagger_schemas import *
from drf_yasg.utils import swagger_auto_schema
import orjson
from django.http import HttpResponse
from django.core.files.storage import default_storage
from audio_management.models import AudioTrack
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import *
from .serializers import CompetitionSerializer, CompetitionParticipantSerializer
from audio_management.serializers import AudioTrackSerializer
from rest_framework.permissions import IsAuthenticated


class CompetitionPagination(PageNumberPagination):
    page_size = 10  # Set the default page size
    page_size_query_param = 'page_size'
    max_page_size = 100

class ChallengeList(generics.ListAPIView):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    pagination_class = CompetitionPagination

    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)
            return Response({
                'success': True,
                'data': response.data,
                'message': 'Successfully retrieved'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class CompetitionAudioListView(generics.ListAPIView):
    serializer_class = AudioTrackSerializer
    
    def get_queryset(self):
        competition_id = self.kwargs['competition_id']
        competition_audios = CompetitionAudio.objects.filter(competition_id=competition_id)
        audio_ids = competition_audios.values_list('audio_id', flat=True)
        return AudioTrack.objects.filter(id__in=audio_ids)  

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            
            'data': serializer.data,
            'message': 'Audio tracks retrieved successfully.'
        }, status=status.HTTP_200_OK)

class CompetitionCreateView(generics.CreateAPIView):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Competition created successfully.'
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class DeleteCompetition(APIView):
    def delete(self, request, competition_id):
        try:
            competition = Competition.objects.get(id=competition_id)
            competition.delete()
            return Response({
                'success': True,
                'message': "Competition deleted successfully."
            }, status=status.HTTP_204_NO_CONTENT)
        except Competition.DoesNotExist:
            return Response({
                'success': False,
                'error': "Competition not found."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CompetitionParticipantCreateView(generics.CreateAPIView):
    queryset = CompetitionParticipant.objects.all()
    serializer_class = CompetitionParticipantSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Participant created successfully.'
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class CompetitionParticipantScoreView(generics.UpdateAPIView):
    queryset = CompetitionParticipant.objects.all()
    serializer_class = CompetitionParticipantSerializer

    def update(self, request, *args, **kwargs):
        competition_id = self.kwargs['competition_id'] 
        participant_id = self.kwargs['pk'] 

        try:

            participant = self.get_queryset().get(id=participant_id, competition_id=competition_id)

            # Update the participant's score
            participant.participant_score = request.data.get('participant_score', participant.participant_score)
            participant.save()

            return Response({
                'success': True,
                'data': {'participant_score': participant.participant_score},
                'message': 'Participant score updated successfully.'
            }, status=status.HTTP_200_OK)
        except CompetitionParticipant.DoesNotExist:
            return Response({
                'success': False,
                'error': "Participant not found in the specified competition."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TopParticipantsPagination(PageNumberPagination):
    page_size = 10  

class TopParticipantsListView(generics.ListAPIView):
    queryset = CompetitionParticipant.objects.all().order_by('-participant_score')
    serializer_class = CompetitionParticipantSerializer
    pagination_class = TopParticipantsPagination

    def get_queryset(self):
        competition_id = self.kwargs['competition_id']
        return super().get_queryset().filter(competition_id=competition_id)[:10]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Top participants retrieved successfully.'
        }, status=status.HTTP_200_OK)

class UploadCompetitionTracks(APIView):
    parser_classes = [MultiPartParser]
    @swagger_auto_schema(
        operation_description="Uploads an audio file as a reference track and saves it with specified category and difficulty.",
        manual_parameters=audio_upload_parameters,
    )
    def post(self, request):
        audio_file = request.data.get('audio_file')
        competition_id = request.data.get('competition_id')  
        name = request.data.get('name')
        artist = request.data.get('artist')
        description = request.data.get('description')
        category = request.data.get('category')
        difficulty_level = request.data.get('difficulty_level')
        genre = request.data.get('genre')  
        musical_element = request.data.get('musical_element')
        music_length = request.data.get('music_length')  

        try:
            if not audio_file or not competition_id or not category or not difficulty_level or not genre or not musical_element or not music_length:
                return Response(
                    {"error": "All fields (audio_file, competition_id, category, difficulty_level, genre, musical_element, music_length) are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            
            file_path = default_storage.save(audio_file.name, audio_file)
            
            
            reference_track = AudioTrack(
                audio_file=file_path,
                name=name,
                artist=artist,
                description=description,
                category=category,
                difficulty_level=difficulty_level,
                genre=genre,  
                musical_element=musical_element, 
                music_length=music_length  #
            )
            reference_track.save()

            
            competition_audio = CompetitionAudio(
                competition_id=competition_id,
                audio_id=reference_track
            )
            competition_audio.save()

            return Response(
                {'success': True, 'message': "Reference track uploaded successfully.", "track_id": reference_track.id},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)
        


class AddExistingAudioToCompetition(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Adds an existing audio track to a competition.",
        request_body=add_existing_competition_audio_schema,  
    )

    
    def post(self, request):
        if not request.user.role=='Admin':
            return Response({'success':False,'error' : "You are not authorized to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
        competition_id = request.data.get('competition_id')
        audio_id = request.data.get('audio_id')

        try:
            if not competition_id or not audio_id:
                return Response(
                    {"error": "Both competition_id and audio_id are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if the competition exists
            competition = Competition.objects.get(id=competition_id)
            # Check if the audio track exists
            audio_track = AudioTrack.objects.get(id=audio_id)

            # Create the mapping between competition and audio
            competition_audio = CompetitionAudio(
                competition_id=competition,
                audio_id=audio_track
            )
            competition_audio.save()

            return Response(
                {'success': True, 'message': "Competition audio added successfully."},
                status=status.HTTP_201_CREATED
            )
        except Competition.DoesNotExist:
            return Response(
                {'success': False, 'error': "Competition not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except AudioTrack.DoesNotExist:
            return Response(
                {'success': False, 'error': "Audio track not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)