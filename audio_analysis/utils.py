import numpy as np
import essentia.standard as es
from essentia import Pool, array
import os
import json
import asyncio
import multiprocessing as mp
from essentia.standard import *
import orjson
from django.http import HttpResponse
import numpy as np
from .tasks import *
import openai
from pydantic import BaseModel
from openai import OpenAI
from openai import OpenAI
from pydantic import BaseModel
from decouple import config


# Define your API key securely
API_KEY = config("API_KEY")

import essentia.standard as estd

def compare_audio_files(query_audio_path, reference_audio_path, alignment_type='serra09', distance_type='asymmetric'):
    """
    Compare two audio files (query and reference) and compute a cover song similarity score.
    
    Parameters:
    query_audio_path (str): Path to the query audio file (cover song).
    reference_audio_path (str): Path to the reference audio file (true or false cover).
    alignment_type (str): Sequence alignment type ('serra09', 'chen17', etc.).
    distance_type (str): Distance type for the similarity measure ('asymmetric', 'symmetric').
    
    Returns:
    float: Cover song similarity distance.
    """
    # Load audio files and convert to mono
    query_audio = estd.MonoLoader(filename=query_audio_path, sampleRate=32000)()
    reference_audio = estd.MonoLoader(filename=reference_audio_path, sampleRate=32000)()

    # Compute Harmonic Pitch Class Profile (HPCP)
    query_hpcp = estd.hpcpgram(query_audio, sampleRate=32000)
    reference_hpcp = estd.hpcpgram(reference_audio, sampleRate=32000)
    
    # Compute Chroma Cross Similarity
    crp = estd.ChromaCrossSimilarity(frameStackSize=9,
                                     frameStackStride=1,
                                     binarizePercentile=0.095,
                                     oti=True)
    
    # Compute cross recurrent plot for the query and reference pair
    crp_result = crp(query_hpcp, reference_hpcp)
    
    # Plot the cross recurrent plot

    # Compute the Cover Song Similarity distance using the precomputed cross similarity
    score_matrix, distance = estd.CoverSongSimilarity(disOnset=0.5,
                                                      disExtension=0.5,
                                                      alignmentType=alignment_type,
                                                      distanceType=distance_type)(crp_result)
    
    return distance

def extract_music_extractor_features(audio_path):
    """
    Extracts audio features using Essentia's MusicExtractor for more advanced feature extraction.

    Parameters:
    - audio_path (str): Path to the audio file.

    Returns:
    - dict: A dictionary containing the parsed audio features in a JSON-serializable format.
    """
    def _extract_music_features():
        """
        Synchronously extracts music features using MusicExtractor.
        """
        features, _ = MusicExtractor(
            lowlevelStats=['mean', 'stdev'],
            rhythmStats=['mean', 'stdev'],
            tonalStats=['mean', 'stdev']
        )(audio_path)
        return features

    def _parse_music_extractor_features(features):
        """
        Helper function to parse and convert the MusicExtractor features into a JSON-serializable format.
        """
        def convert_to_serializable(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj

        features_dict = {
            "loudness_ebu128": {
                "integrated": convert_to_serializable(features['lowlevel.loudness_ebu128.integrated']),
                "loudness_range": convert_to_serializable(features['lowlevel.loudness_ebu128.loudness_range'])
            },
            "mfcc_mean": convert_to_serializable(features['lowlevel.mfcc.mean']),
            "tempo": convert_to_serializable(features['rhythm.bpm']),
            "beat_positions": convert_to_serializable(features['rhythm.beats_position']),
            "key_scale": {
                "key": convert_to_serializable(features['tonal.key_edma.key']),
                "scale": convert_to_serializable(features['tonal.key_edma.scale'])
            },
            "spectral_complexity": {
                "mean": convert_to_serializable(features['lowlevel.spectral_complexity.mean']),
                "stdev": convert_to_serializable(features['lowlevel.spectral_complexity.stdev'])
            },
            "dynamic_complexity": convert_to_serializable(features['lowlevel.dynamic_complexity']),
            "spectral_contrast": {
                "spectral_contrast_mean": convert_to_serializable(features['lowlevel.spectral_contrast_coeffs.mean']),
                "spectral_contrast_std": convert_to_serializable(features['lowlevel.spectral_contrast_coeffs.stdev'])
            },
            'zero_crossing_rate': {
                'zero_crossing_rate_mean': convert_to_serializable(features['lowlevel.zerocrossingrate.mean']),
                'zero_crossing_rate_std': convert_to_serializable(features['lowlevel.zerocrossingrate.stdev']),
            },
            'key_detection': {
                'key_edma': convert_to_serializable(features['tonal.key_edma.key']),
                'key_krumhansl': convert_to_serializable(features['tonal.key_krumhansl.key']),
                'key_temperley': convert_to_serializable(features['tonal.key_temperley.key']),
            }
        }

        return features_dict

    # Extract features and parse them
    features = _extract_music_features()
    return _parse_music_extractor_features(features)
# '''Define the response model using Pydantic

'''

class AudioAnalysis(BaseModel):
    score: int
    reasoning: str'''

class AudioAnalysis(BaseModel):
    genre: str
    instrument:str
    vocal_style:str

def get_chat_gpt_response(prompt: str) -> AudioAnalysis:
    """Get a structured response from the GPT-4 API."""
    try:
        # Initialize the OpenAI client
        client = OpenAI(api_key=API_KEY)

        # Create the conversation messages
        messages = [
            {"role": "system", "content": "Analyze the user audio performance."},
            {"role": "user", "content": prompt},
        ]

        # Request completion from the API
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=messages,
            response_format=AudioAnalysis,
        )

        # Extract and return the parsed response
        return completion.choices[0].message.parsed

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def orjson_response(data):
    # Convert any numpy types to native Python types
    if isinstance(data, np.ndarray):
        data = data.tolist()  # Convert the whole array to a list
    elif isinstance(data, (np.float32, np.float64)):
        data = float(data)  # Convert to a native Python float
    # Add more conversions as needed for other NumPy types
    return orjson.dumps(data)


def extract_essentia_features(full_file_path):

    basic_features_result = extract_basic_features.delay(full_file_path)
    chroma_features_result = extract_chroma.delay(full_file_path)
    extract_loudness_result = extract_loudness.delay(full_file_path)
    extract_tempo_and_beat_postions_result = extract_tempo_and_beat_postions.delay(
        full_file_path
    )
    extract_key_and_scale_result = extract_key_and_scale.delay(full_file_path)
    envelope_shape_result = extract_envelope_shape.delay(full_file_path)
    avg_harmonic_ratio_result = extract_harmonic_ratio.delay(full_file_path)
    mfcc_result = extract_mfcc.delay(full_file_path)
    dynamic_complexity_result = extract_dynamic_complexity.delay(full_file_path)
    spectral_complexity_result = extract_spectral_complexity.delay(full_file_path)
    zero_crossing_rate_result = extract_zero_crossing_rate.delay(full_file_path)
    spectral_contrast_result = extract_spectral_contrast.delay(full_file_path)

    # Get the results (or handle asynchronously)
    basic_features = basic_features_result.get()
    chroma_features = chroma_features_result.get()
    loudness_features = extract_loudness_result.get()
    tempo_and_beat_positions = extract_tempo_and_beat_postions_result.get()
    key_and_scale = extract_key_and_scale_result.get()
    envelope_shape = envelope_shape_result.get()
    avg_harmonic_ratio = avg_harmonic_ratio_result.get()
    mfcc = mfcc_result.get()
    dynamic_complexity = dynamic_complexity_result.get()
    spectral_complexity = spectral_complexity_result.get()
    zero_crossing_rate = zero_crossing_rate_result.get()
    spectral_contrast = spectral_contrast_result.get()

    response_data = {
        "basic_features": basic_features,
        "chroma_features": chroma_features,
        "envelope_shape": envelope_shape,
        "avg_harmonic_ratio": avg_harmonic_ratio,
        "mfcc": mfcc,
        "loudness_features": loudness_features,
        "tempo_and_beat_positions": tempo_and_beat_positions,
        "key_and_scale": key_and_scale,
        "dynamic_complexity": dynamic_complexity,
        "spectral_complexity": spectral_complexity,
        "zero_crossing_rate": zero_crossing_rate,
        "spectral_contrast": spectral_contrast,
    }

    return response_data
