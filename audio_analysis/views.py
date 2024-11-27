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
from essentia.standard import MonoLoader, PitchCREPE
from essentia.standard import MonoLoader, TensorflowPredictEffnetDiscogs, TensorflowPredict2D
from essentia.standard import MonoLoader, TensorflowPredictMusiCNN, TensorflowPredictVGGish
import os

class CompareTwoAudiosEndpoint(APIView):
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_description="Uploads two audio files (reference and query) and compares their features with unique insight from AI.",
        manual_parameters=compare_audio_upload_parameters,
    )
    def post(self, request):
        ref_audio_path = query_audio_path = None
        if "query_file" not in request.FILES or "reference_file" not in request.FILES:
            return Response({"success": False, "error": "Missing audio files."}, status=status.HTTP_400_BAD_REQUEST)
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
            audio = MonoLoader(filename=query_audio_full_path, sampleRate=16000, resampleQuality=4)()
            
            graph_file_path = os.path.abspath("discogs-effnet-bs64-1.pb")
            return Response(graph_file_path)
            embedding_model = TensorflowPredictEffnetDiscogs(graphFilename='discogs-effnet-bs64-1.pb', output="PartitionedCall:1")
            embeddings = embedding_model(audio)
            model = TensorflowPredict2D(graphFilename="mtg_jamendo_instrument-discogs-effnet-1.pb")
            predictions = model(embeddings) 
            return Response(predictions) 

            #ref_audio_features = extract_essentia_features(ref_audio_full_path)
            start_time=time.time()
            file1="discogs-effnet-bs64-1.pb"
            return Response({'data':self.predict_instrument(query_audio_full_path)}) 
            query_audio_features = extract_music_extractor_features(query_audio_full_path)
            distance = compare_audio_files(request.FILES["query_file"],request.FILES["reference_file"])

            end_time=time.time() 
            return Response({'distance':distance,'time':end_time-start_time})
            # Use ThreadPoolExecutor to run feature extraction concurrently

            # Generate a prompt for the AI model
            return Response({'response':query_audio_features,'time_spent':end_time-start_time})
            prompt2 = analyse_sound(query_audio_features) 
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
    
    def analyze_audio(self,audio_path):
        """
        Analyzes an audio file using Essentia's TensorFlow-based models to detect
        musical instruments and classify music vs non-music.
        
        Parameters:
            audio_path (str): Path to the audio file
            
        Returns:
            dict: Analysis results containing instrument predictions and music/noise classification
        """
        # Load audio file
        loader = es.MonoLoader(filename=str(audio_path))
        audio = loader()
        
        # Initialize TensorFlow-based models
        instrument_classifier = es.TensorflowPredict(
            graphFilename='musicnn-mtt-musicnn-1.pb',
            input='model/Placeholder',
            output='model/Sigmoid'
        )
        
        # Initialize feature extractors needed by the model
        patch_size = 187
        patch_hop_size = 128
        frame_size = 512
        hop_size = 256
        
        # Extract features using VGGish model requirements
        features = []
        for frame in es.FrameGenerator(audio, frameSize=frame_size, hopSize=hop_size):
            features.append(frame)
        
        # Get predictions
        predictions = instrument_classifier(features)
        
        # Get top predicted instruments (threshold > 0.5)
        instrument_labels = [
            'guitar', 'piano', 'drums', 'violin', 'cello', 'flute', 
            'saxophone', 'trumpet', 'voice', 'synthesizer'
        ]
        
        detected_instruments = []
        confidence_scores = {}
        
        for i, score in enumerate(predictions[0]):
            confidence_scores[instrument_labels[i]] = float(score)
            if score > 0.5:
                detected_instruments.append(instrument_labels[i])
        
        # Use music/non-music classifier
        music_classifier = es.MusicExtractor()
        music_features, _ = music_classifier(str(audio_path))
        
        # Determine if it's music based on several musical features
        is_music = music_features['is_music']
        
        return {
            'is_music': bool(is_music),
            'detected_instruments': detected_instruments,
            'confidence_scores': confidence_scores
        }
    
    def extract_pitch(self, audio_path): 
        sample_rate = 44100
        audio = es.MonoLoader(filename=audio_path, sampleRate=sample_rate)()
        pExt = es.PredominantPitchMelodia(frameSize=2048, hopSize=128)
        pitch, pitchConf = pExt(audio)
        return len(pitch), len(pitchConf) 
    
    def predict_instrument(self,audio_path,file1,file2):
        audio = MonoLoader(filename=audio_path, sampleRate=16000, resampleQuality=4)()
        embedding_model = TensorflowPredictEffnetDiscogs(graphFilename="discogs-effnet-bs64-1.pb", output="PartitionedCall:1")
        embeddings = embedding_model(audio)
        model = TensorflowPredict2D(graphFilename="mtg_jamendo_instrument-discogs-effnet-1.pb")
        predictions = model(embeddings)
        return predictions 