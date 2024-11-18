from django.shortcuts import render
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
from .models import Challenge, ChallengeParticipant, ChallengeAudio
from .serializers import ChallengeSerializer, ChallengeParticipantSerializer
from audio_management.serializers import AudioTrackSerializer



class ChallengeAudioListView(generics.ListAPIView):
    serializer_class = AudioTrackSerializer
    def get_queryset(self):
        challenge_id = self.kwargs['challenge_id']
        challenge_audios = ChallengeAudio.objects.filter(challenge_id=challenge_id)
        audio_ids = challenge_audios.values_list('audio_id', flat=True)
        return AudioTrack.objects.filter(id__in=audio_ids)  

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            
            'data': serializer.data,
            'message': 'Audio tracks retrieved successfully.'
        }, status=status.HTTP_200_OK)

class ChallengeCreateView(generics.CreateAPIView):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Challenge created successfully.'
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class DeleteChallenge(APIView):
    def delete(self, request, challenge_id):
        try:
            challenge = Challenge.objects.get(id=challenge_id)
            challenge.delete()
            return Response({
                'success': True,
                'message': "Challenge deleted successfully."
            }, status=status.HTTP_204_NO_CONTENT)
        except Challenge.DoesNotExist:
            return Response({
                'success': False,
                'error': "Challenge not found."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChallengeParticipantCreateView(generics.CreateAPIView):
    queryset = ChallengeParticipant.objects.all()
    serializer_class = ChallengeParticipantSerializer

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

class ChallengeParticipantScoreView(generics.UpdateAPIView):
    queryset = ChallengeParticipant.objects.all()
    serializer_class = ChallengeParticipantSerializer

    def update(self, request, *args, **kwargs):
        challenge_id = self.kwargs['challenge_id'] 
        participant_id = self.kwargs['pk'] 

        try:

            participant = self.get_queryset().get(id=participant_id, challenge_id=challenge_id)

            # Update the participant's score
            participant.participant_score = request.data.get('participant_score', participant.participant_score)
            participant.save()

            return Response({
                'success': True,
                'data': {'participant_score': participant.participant_score},
                'message': 'Participant score updated successfully.'
            }, status=status.HTTP_200_OK)
        except ChallengeParticipant.DoesNotExist:
            return Response({
                'success': False,
                'error': "Participant not found in the specified challenge."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TopParticipantsPagination(PageNumberPagination):
    page_size = 10  

class TopParticipantsListView(generics.ListAPIView):
    queryset = ChallengeParticipant.objects.all().order_by('-participant_score')
    serializer_class = ChallengeParticipantSerializer
    pagination_class = TopParticipantsPagination

    def get_queryset(self):
        challenge_id = self.kwargs['challenge_id']
        return super().get_queryset().filter(challenge_id=challenge_id)[:10]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Top participants retrieved successfully.'
        }, status=status.HTTP_200_OK)

class UploadChallengeTracks(APIView):
    parser_classes = [MultiPartParser]
    @swagger_auto_schema(
        operation_description="Uploads an audio file as a reference track for a challenge and saves it with specified category and difficulty.",
        manual_parameters=audio_upload_parameters,
    )
    def post(self, request,**kwargs):
        audio_file = request.data.get('audio_file')
        challenge_id = kwargs['challenge_id']  
        name = request.data.get('name')
        artist = request.data.get('artist')
        description = request.data.get('description')
        category = request.data.get('category')
        difficulty_level = request.data.get('difficulty_level')
        genre = request.data.get('genre')  
        musical_element = request.data.get('musical_element')
        music_length = request.data.get('music_length')  

        try:
            if not audio_file or not challenge_id or not category or not difficulty_level or not genre or not musical_element or not music_length:
                return Response(
                    {"error": "All fields (audio_file, challenge_id, category, difficulty_level, genre, musical_element, music_length) are required."},
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

            
            challenge_audio = ChallengeAudio(
                challenge_id=challenge_id,
                audio_id=reference_track
            )
            challenge_audio.save()

            return Response(
                {'success': True, 'message': "Reference track uploaded successfully.", "audio_id": reference_track.id},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)
        


class AddExistingAudioToChallenge(APIView):
    @swagger_auto_schema(
        operation_description="Adds an existing audio track to a challenge.",
        request_body=add_existing_challenge_audio_schema,  
    )
    def post(self, request):
        challenge_id = request.data.get('challenge_id')
        audio_id = request.data.get('audio_id')

        try:
            if not challenge_id or not audio_id:
                return Response(
                    {"error": "Both challenge_id and audio_id are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            
            challenge = Challenge.objects.get(id=challenge_id)
            #return Response(challenge.name)
            
            audio_track = AudioTrack.objects.get(id=audio_id)

            #
            challenge_audio = ChallengeAudio(
                challenge=challenge,
                audio_id=audio_track
            )
            challenge_audio.save()

            return Response(
                {'success': True, 'message': "Challenge audio added successfully."},
                status=status.HTTP_201_CREATED
            )
        except Challenge.DoesNotExist:
            return Response(
                {'success': False, 'error': "Challenge not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except AudioTrack.DoesNotExist:
            return Response(
                {'success': False, 'error': "Audio track not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            #raise e
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChallengePagination(PageNumberPagination):
    page_size = 10  # Set the default page size
    page_size_query_param = 'page_size'
    max_page_size = 100

class ChallengeList(generics.ListAPIView):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer
    pagination_class = ChallengePagination

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

class UserChallenges(generics.ListAPIView):
    serializer_class = ChallengeSerializer
    pagination_class = ChallengePagination

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Challenge.objects.filter(created_by__id=user_id)

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

