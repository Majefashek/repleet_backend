from celery import shared_task 
from time import sleep
import essentia.standard as es
from essentia import Pool, array
import os
import json
import asyncio
import multiprocessing as mp
from essentia.standard import *
import orjson
from django.http import HttpResponse
import orjson
import numpy as np
import essentia
import essentia.streaming as ess

#ranspose to have it in a better shape
# we need to convert the list to an essentia.array first (== numpy.array of floats)

@shared_task
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
        features, _ = es.MusicExtractor(
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
@shared_task
def extract_basic_features(audio_path):
    
    # Check if the provided audio path exists and is a valid file
    if not os.path.isfile(audio_path):
        raise ValueError(f"Invalid audio path: {audio_path} does not exist or is not a file.")
    
    print(f'Processing audio file: {audio_path}')
    

    
    # Load audio
    audio = es.MonoLoader(filename=audio_path)()
    pExt = es.PredominantPitchMelodia(frameSize=2048, hopSize=128)
    pitch, pitchConf = pExt(audio) 
    pitch_yin_fft = es.PitchYinFFT()(audio)
    # Return the extracted features
    return {
        "fundamental_frequency": {
            "pitch_yin_fft":pitch_yin_fft[0],  # tuple (pitch_yin_fft, pitch_confidence)
            "pitch_confidence":pitch_yin_fft[1] 
        },      
    }
'''
def extract_envelope(self, audio):
    """
    Extracts the envelope shape of the audio.

    """
    data=Envelope()(audio)
    return data.tolist() '''

@shared_task
def extract_chroma(audio_path, frame_length=32768, overlap=16384):
        """
        Extracts the chroma features from the audio using overlapping frames.
        
        Parameters:
        - audio: The audio signal to process.
        - frame_length: The length of each frame in samples (default is 32,768 samples).
        - overlap: The number of samples to overlap between frames (default is 16,384 samples).
        
        Returns:
        - A list of chroma feature arrays for each frame.
        """
        # Initialize the algorithms
        audio = es.MonoLoader(filename=audio_path)()
        w = es.Windowing(type='hann')
        spectrum = es.Spectrum()
        chromagram = es.Chromagram(numberBins=84, binsPerOctave=12)

        # Check if the audio is long enough
        if len(audio) < frame_length:
            raise ValueError("Audio file is too short to extract chroma features.")
        
        chroma_features = []
        num_frames = (len(audio) - frame_length) // overlap + 1

        # Loop through the audio to create overlapping frames
        for i in range(num_frames):
            start = i * overlap
            end = start + frame_length * 2 - 2

            # Extract the current frame
            frame = audio[start:end]

            # Ensure the frame length is even
            if len(frame) % 2 != 0:
                frame = frame[:-1]  # Trim the last sample if odd

            # If the frame is shorter than frame_length after trimming, skip it
            if len(frame) < frame_length:
                continue

            try:
                # Compute the spectrum for the frame
                spec = spectrum(w(frame))

                # Compute the chromagram
                chroma_values = float(chromagram(spec).mean())

                # Append the chroma values to the list
                chroma_features.append(chroma_values)

            except RuntimeError as e:
                # Handle the specific error related to FFT size
                if "FFT: can only compute FFT of arrays which have an even size" in str(e):
                    print("Skipping frame due to FFT size error.")
                    continue
                
        data={"chroma":chroma_features}  # Skip the current frame and continue with the next

        return data    

@shared_task
def extract_envelope_shape(audio_path):
    audio = es.MonoLoader(filename=audio_path)()
    envelope_shape=float(es.Envelope()(audio).mean())
    return envelope_shape

@shared_task
def extract_harmonic_ratio(audio_path):
    """
    Extracts the harmonic ratio of an audio signal using Essentia, processing each frame independently.
    
    Parameters:
    audio_path (str): Path to the input audio file.
    
    Returns:
    float: The harmonic ratio (average over frames).
    """
    sample_rate = 44100
    frame_size = 2048
    harmonics_count = 5

    # Load the audio file
    audio = es.MonoLoader(filename=audio_path)()

    # Step 1: Pitch and Spectrum Extraction Setup
    window = es.Windowing(type='hann')
    fft = es.FFT()  # Complex FFT
    cartesian_to_polar = es.CartesianToPolar()  # Converts complex to magnitude/phase
    pitch_extractor = es.PitchYinFFT()
    
    harmonic_ratios = []
    
    # Step 2: Process each frame
    for frame in es.FrameGenerator(audio, frameSize=frame_size, hopSize=frame_size//2, startFromZero=True):
        # Apply windowing and compute FFT
        windowed_frame = window(frame)
        fft_frame = fft(windowed_frame)
        
        # Convert complex FFT output to magnitude (ignore phase for this task)
        magnitude, phase = cartesian_to_polar(fft_frame)
        
        # Step 3: Extract pitch for the current frame
        pitch, pitch_confidence = pitch_extractor(frame)
        
        if pitch == 0 or pitch_confidence < 0.5:
            # Skip frames with no reliable pitch
            continue
        
        # Step 4: Identify harmonics based on the current frame's pitch
        harmonics = [pitch * n for n in range(1, harmonics_count + 1)]  # First N harmonics
        
        # Step 5: Convert harmonic frequencies to corresponding FFT bins and calculate energies
        def freq_to_bin(freq, sr, frame_size):
            return int(np.round(freq * frame_size / sr))
        
        total_energy = np.sum(magnitude)
        harmonic_energy = 0
        
        for harmonic in harmonics:
            harmonic_bin = freq_to_bin(harmonic, sample_rate, frame_size)
            if harmonic_bin < len(magnitude):
                # Sum the energy of nearby bins (to account for inaccuracies)
                harmonic_energy += np.sum(magnitude[max(0, harmonic_bin-1):min(harmonic_bin+2, len(magnitude))])
        
        # Step 6: Calculate the harmonic ratio for the current frame
        if total_energy > 0:
            harmonic_ratio = harmonic_energy / total_energy
            harmonic_ratios.append(harmonic_ratio)
    
    # Step 7: Return the average harmonic ratio across all valid frames
    return np.mean(harmonic_ratios) if harmonic_ratios else 0.0



def orjson_response(data):
    if isinstance(data, np.ndarray):
        data = data.tolist()  # Convert the whole array to a list
    elif isinstance(data, (np.float32, np.float64)):
        data = float(data)  
    return HttpResponse(
        orjson.dumps(data),
        content_type='application/json'
    )