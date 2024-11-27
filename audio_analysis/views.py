from io import BytesIO
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from pydub import AudioSegment
from .swagger_schemas import compare_audio_upload_parameters
from drf_yasg.utils import swagger_auto_schema 
from .prompt import *
from .utils import *
import uuid  # Import uuid to generate unique filenames
from concurrent.futures import ProcessPoolExecutor
import time
import os

class CompareTwoAudiosEndpoint(APIView):
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_description="Uploads two audio files (reference and query) and compares their features with unique insight from AI.",
        manual_parameters=compare_audio_upload_parameters,
    )
    def post(self, request):
        ref_audio_path = query_audio_path = None
        try:
            # Extract audio files from request
            ref_audio_file = self.trimaudio(request.FILES["reference_file"])
            query_audio_file = self.trimaudio(request.FILES["query_file"])

            ref_audio_filename = f"ref_audio_{uuid.uuid4()}.mp3"
            query_audio_filename = f"query_audio_{uuid.uuid4()}.mp3"

            # Save uploaded audio files temporarily
            ref_audio_path = default_storage.save(ref_audio_filename, ref_audio_file)
            query_audio_path = default_storage.save(
                query_audio_filename, query_audio_file
            )

            # Get full paths to the audio files
            ref_audio_full_path = default_storage.path(ref_audio_path)
            query_audio_full_path = default_storage.path(query_audio_path)

            ref_audio_features = extract_essentia_features(ref_audio_full_path)
            query_audio_features = extract_essentia_features(query_audio_full_path)

            # Use ThreadPoolExecutor to run feature extraction concurrently

            # Generate a prompt for the AI model
            prompt2 = newest_prompt(ref_audio_features, query_audio_features)
            response = get_chat_gpt_response(prompt2)
            response_dict = {item[0]: item[1] for item in response}

            return Response({"success": True, "ai_response": response_dict}, status=200)

        except Exception as e:
            raise e
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        finally:
            # Delete temporary audio files after processing
            if ref_audio_path:
                default_storage.delete(ref_audio_path)
            if query_audio_path:
                default_storage.delete(query_audio_path)

    def trimaudio(self, audio):
        audio_untrimmed = AudioSegment.from_file(audio)
        time = 30 * 1000
        trimmed_audio = audio_untrimmed[:time]
        output = BytesIO()
        trimmed_audio.export(output, format="mp3")
        output.seek(0)
        return output