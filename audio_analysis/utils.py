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


# Define the response model using Pydantic
class AudioAnalysis(BaseModel):
    score: int
    recommendation: str


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
