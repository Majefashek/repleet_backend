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
from .tasks import  extract_basic_features, extract_chroma,extract_music_extractor_features
import openai
from pydantic import BaseModel
from openai import OpenAI
from openai import OpenAI
from pydantic import BaseModel
from decouple import config


# Define your API key securely
API_KEY = config("API_KEY")
import essentia.standard as estd

def process_arr(arr):
        n=len(arr)
        m=len(arr[0])
        res=[]
        for i in range(m):
            summ=0
            for j in range(n):
                summ+=arr[j][i]
            res.append(summ/n)
        return res



def get_top_three_instruments(probabilities):
    """
    Returns the top three instruments with the highest probabilities.
    
    Parameters:
        probabilities (dict): A dictionary with instruments as keys and probabilities as values.
    
    Returns:
        list: A list of tuples containing the top three instruments and their probabilities.
    """
    # Sort the dictionary by values in descending order and get the top three
    top_three = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)[:3]
    return top_three
    
def predict_instrument(audio_path):
    audio = es.MonoLoader(filename=audio_path, sampleRate=16000, resampleQuality=4)()
    embedding_model = es.TensorflowPredictEffnetDiscogs(graphFilename="/app/discogs-effnet-bs64-1.pb", output="PartitionedCall:1")
    embeddings = embedding_model(audio)
    model = es.TensorflowPredict2D(graphFilename="/app/mtg_jamendo_instrument-discogs-effnet-1.pb")
    predictions = model(embeddings)
    data=process_arr(predictions)
    instruments = [
        "accordion", "acousticbassguitar", "acousticguitar", "bass", "beat", 
        "bell", "bongo", "brass", "cello", "clarinet", "classicalguitar", 
        "computer", "doublebass", "drummachine", "drums", "electricguitar", 
        "electricpiano", "flute", "guitar", "harmonica", "harp", "horn", 
        "keyboard", "oboe", "orchestra", "organ", "pad", "percussion", 
        "piano", "pipeorgan", "rhodes", "sampler", "saxophone", "strings", 
        "synthesizer", "trombone", "trumpet", "viola", "violin", "voice"
    ]
    mydic={}
    for k,v in zip(instruments,data):
        mydic[k]=v
    
    return get_top_three_instruments(mydic) 







def calculate_similarity(query, ref): 
    """
    Compares instruments between the query and ref tracks to determine similarity using a
    combination of naming similarity and probability-weighted similarity.

    Parameters:
        query (list): A list of instruments and their probabilities from the query track.
        ref (list): A list of instruments and their probabilities from the ref track.

    Returns:
        dict: A result containing similarity percentage, weighted similarity, and match status.
    """
    # Extract instruments and probabilities
    query_instruments = {item[0]: item[1] for item in query}
    ref_instruments = {item[0]: item[1] for item in ref}

    # Find all unique instruments
    all_instruments = set(query_instruments.keys()) | set(ref_instruments.keys())

    # Calculate naming similarity (intersection / union)
    matching_instruments = set(query_instruments.keys()) & set(ref_instruments.keys())
    naming_similarity = len(matching_instruments) / len(all_instruments) if all_instruments else 0

    # Calculate probability-weighted similarity
    weighted_similarity = sum(
        query_instruments.get(instr, 0) * ref_instruments.get(instr, 0)
        for instr in all_instruments
    )

    # Combine naming similarity and weighted similarity

    # Determine if the tracks are considered similar
    is_similar= naming_similarity >= 0.5 or weighted_similarity >= 0.5
    

    return {
        "is_similar": is_similar,
        "combined_similarity":is_similar
    }


# '''Define the response model using Pydantic

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
        return str(e)
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
    extract_music_extractor_features_result=extract_music_extractor_features.delay(full_file_path)

    

    # Get the results (or handle asynchronously)
    basic_features = basic_features_result.get()
    chroma_features = chroma_features_result.get()
    extract_music_extractor_features_=extract_music_extractor_features_result.get()

   
    response_data = {
        "basic_features": basic_features,
        "chroma_features": chroma_features,
        "mfcc": extract_music_extractor_features_["mfcc_mean"],
        "loudness_features": extract_music_extractor_features_["loudness_ebu128"],
        "tempo":extract_music_extractor_features_["tempo"],
        "beat_positions":extract_music_extractor_features_["beat_positions"],
        "key_and_scale":extract_music_extractor_features_[ "key_scale"],
        "dynamic_complexity":extract_music_extractor_features_["dynamic_complexity"],
        "spectral_complexity": extract_music_extractor_features_["spectral_complexity"],
        "zero_crossing_rate":extract_music_extractor_features_["zero_crossing_rate"],
        "spectral_contrast": extract_music_extractor_features_["spectral_contrast"],
    }

    return response_data

    '''
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
    }'''
    return response_data

'''
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
'''

'''
 tempo_and_beat_positions = extract_tempo_and_beat_postions_result.get()
    key_and_scale = extract_key_and_scale_result.get()
    envelope_shape = envelope_shape_result.get()
    avg_harmonic_ratio = avg_harmonic_ratio_result.get()
    mfcc = mfcc_result.get()
    dynamic_complexity = dynamic_complexity_result.get()
    spectral_complexity = spectral_complexity_result.get()
    zero_crossing_rate = zero_crossing_rate_result.get()
    spectral_contrast = spectral_contrast_result.get()

'''