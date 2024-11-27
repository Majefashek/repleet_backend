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
print("Numpy imported: ", np.__version__)


@shared_task
def extract_spectral_contrast(audio_path, frame_size=2048, hop_size=512, 
                              sample_rate=22050, low_freq_bound=20, 
                              high_freq_bound=11000, num_bands=6):
    """
    Extracts spectral contrast features from the input audio file.

    Parameters:
    audio_path (str): Path to the input audio file.
    frame_size (int): Size of each frame in samples (default=2048).
    hop_size (int): Number of samples to shift between consecutive frames (default=512).
    sample_rate (int): Sampling rate of the audio file (default=22050).
    low_freq_bound (float): Lower bound for the lowest band (default=20 Hz).
    high_freq_bound (float): Upper bound for the highest band (default=11000 Hz).
    num_bands (int): Number of frequency bands (default=6).

    Returns:
    dict: A dictionary containing the mean and standard deviation of spectral contrast per band.
    """
    # Load the audio file
    audio = MonoLoader(filename=audio_path, sampleRate=sample_rate)()

    # Initialize processors with the given parameters
    windowing = Windowing(type='hann')
    spectrum = Spectrum()
    spectral_contrast = SpectralContrast(
        lowFrequencyBound=low_freq_bound,
        highFrequencyBound=high_freq_bound,
        numberBands=num_bands,
        sampleRate=sample_rate
    )

    # Store Spectral Contrast values for all frames
    all_contrast_values = []

    # Process each frame and extract Spectral Contrast
    for frame in FrameGenerator(audio, frameSize=frame_size, hopSize=hop_size, startFromZero=True):
        # Apply windowing and compute the spectrum
        spec = spectrum(windowing(frame))

        # Ensure spectrum size matches frame_size / 2 + 1
        if len(spec) != frame_size // 2 + 1:
            raise ValueError(
                f"Spectrum size mismatch: got {len(spec)}, expected {frame_size // 2 + 1}"
            )

        # Extract spectral contrast coefficients
        contrast_values, _ = spectral_contrast(spec)
        all_contrast_values.append(contrast_values)

    # Convert to NumPy array for easier aggregation
    all_contrast_values = np.array(all_contrast_values)
    print(f'Shape of Spectral Contrast values: {all_contrast_values.shape}')

    # Compute summary statistics (per-band mean/std)
    contrast_mean = np.mean(all_contrast_values, axis=0).tolist()
    contrast_std = np.std(all_contrast_values, axis=0).tolist()

    return {'contrast_mean': contrast_mean, 'contrast_std': contrast_std}

@shared_task
def extract_zero_crossing_rate(audio_path):
    # Load the audio file
    audio = MonoLoader(filename=audio_path)()
    
    # Initialize Zero Crossing Rate extractor
    zcr = ZeroCrossingRate()

    # Store ZCR values for all frames
    all_zcr_values = []

    # Process each frame and extract ZCR
    for frame in FrameGenerator(audio, frameSize=1024, hopSize=512, startFromZero=True):
        zcr_value = zcr(frame)  # ZCR works on raw audio frames
        all_zcr_values.append(zcr_value)

    # Convert to NumPy array for easier aggregation
    all_zcr_values = np.array(all_zcr_values)
    print(f'Shape of ZCR values: {all_zcr_values.shape}')

    # Compute summary statistics
    zcr_mean = np.mean(all_zcr_values).item()
    zcr_std = np.std(all_zcr_values).item()

    return {'zcr_mean': zcr_mean, 'zcr_std': zcr_std}


@shared_task
def extract_spectral_complexity(audio_path):
    # Load the audio file
    audio = MonoLoader(filename=audio_path)()

    # Initialize necessary processors
    w = Windowing(type='hann')
    spectrum = Spectrum()
    spectral_complexity = SpectralComplexity()  # Spectral Complexity extractor

    # Collect all spectral complexity values
    all_complexity_values = []

    # Process each frame and extract spectral complexity
    for frame in FrameGenerator(audio, frameSize=1024, hopSize=512, startFromZero=True):
        spec = spectrum(w(frame))
        complexity_value = spectral_complexity(spec)
        all_complexity_values.append(complexity_value)

    # Convert to NumPy array for easier aggregation
    all_complexity_values = np.array(all_complexity_values)
    print(f'This is the shape of all_complexity_values: {all_complexity_values.shape}')

    # Compute summary statistics across all frames
    complexity_mean = np.mean(all_complexity_values).item()  # Mean of spectral complexity
    complexity_std = np.std(all_complexity_values).item()    # Std of spectral complexity

    return {'complexity_mean': complexity_mean, 'complexity_std': complexity_std}


@shared_task
def extract_dynamic_complexity(audio_file, frame_size=0.2, sample_rate=44100):
    """
    Extracts the dynamic complexity and loudness from an audio file.

    Parameters:
    audio_file (str): Path to the input audio file.
    frame_size (float): Frame size in seconds (default = 0.2).
    sample_rate (int): Sample rate in Hz (default = 44100).

    Returns:
    tuple: (dynamic_complexity, loudness) as floats.
    """

    # Load the audio signal in mono
    audio = es.MonoLoader(filename=audio_file, sampleRate=sample_rate)()

    # Initialize the DynamicComplexity algorithm
    dynamic_complexity_algo = es.DynamicComplexity(
        frameSize=frame_size, sampleRate=sample_rate
    )

    # Compute the dynamic complexity and loudness
    dynamic_complexity, loudness = dynamic_complexity_algo(audio)

    # Return the results
    return dynamic_complexity, loudness


@shared_task
def extract_key_and_scale(audio_path):
    # Initialize algorithms for loading and processing audio
    loader = ess.MonoLoader(filename=audio_path)
    framecutter = ess.FrameCutter(frameSize=4096, hopSize=2048, silentFrames='noise')
    windowing = ess.Windowing(type='blackmanharris62')
    spectrum = ess.Spectrum()
    spectralpeaks = ess.SpectralPeaks(orderBy='magnitude',
                                       magnitudeThreshold=0.00001,
                                       minFrequency=20,
                                       maxFrequency=3500,
                                       maxPeaks=60)

    # HPCP and Key algorithms
    hpcp = ess.HPCP(size=36,  # Use higher resolution for key estimation
                    referenceFrequency=440,
                    bandPreset=False,
                    minFrequency=20,
                    maxFrequency=3500,
                    weightType='cosine',
                    nonLinear=False,
                    windowSize=1.)

    key = ess.Key(profileType='edma',  # Use the electronic music profile
                  numHarmonics=4,
                  pcpSize=36,
                  slope=0.6,
                  usePolyphony=True,
                  useThreeChords=True)

    # Pool to store results
    pool = essentia.Pool()

    # Connect the streaming algorithms
    loader.audio >> framecutter.signal
    framecutter.frame >> windowing.frame >> spectrum.frame
    spectrum.spectrum >> spectralpeaks.spectrum
    spectralpeaks.magnitudes >> hpcp.magnitudes
    spectralpeaks.frequencies >> hpcp.frequencies
    hpcp.hpcp >> key.pcp
    key.key >> (pool, 'tonal.key_key')
    key.scale >> (pool, 'tonal.key_scale')
    key.strength >> (pool, 'tonal.key_strength')

    # Run the streaming network
    essentia.run(loader)

    # Extract the key and scale
    key_result = pool['tonal.key_key']
    scale_result = pool['tonal.key_scale']
             

    
    return {
        "key": key_result,
        "scale": scale_result }


@shared_task
def extract_tempo_and_beat_postions(audio_path):
    audio = es.MonoLoader(filename=audio_path)()
    #Compute beat positions and BPM.
    rhythm_extractor = es.RhythmExtractor2013(method="multifeature")
    bpm, beats,_, _,_ = rhythm_extractor(audio)
    return {'tempo':float(bpm),
            'beat_postions':list(map(float,beats))}

@shared_task
def extract_loudness(audio_path):
    audio_st, _, _, _, _, _ = es.AudioLoader(filename=audio_path)()
    audio_st = es.StereoTrimmer(startTime=0, endTime=30)(audio_st)
    ebu_momentary, ebu_shortterm, ebu_integrated, dr = es.LoudnessEBUR128(hopSize=1024/44100, startAtZero=True)(audio_st)
    return {"Integrated_loudness":ebu_integrated,
            "Dynamic_range":dr}

@shared_task
def extract_mfcc(audio_path):
    audio = MonoLoader(filename=audio_path)()
    w = Windowing(type='hann')
    spectrum = Spectrum()
    mfcc = MFCC(numberCoefficients=13)  # Limiting to 13 coefficients

    # Collect all coefficients
    all_mfcc_coeffs = []

    # Extract MFCCs for each frame
    for frame in FrameGenerator(audio, frameSize=1024, hopSize=512, startFromZero=True):
        _, mfcc_coeffs = mfcc(spectrum(w(frame)))
        all_mfcc_coeffs.append(mfcc_coeffs)

    # Convert to NumPy array for easier aggregation
    all_mfcc_coeffs = np.array(all_mfcc_coeffs)
    print('this is the shape of all_mfcc_coeffs {all_mfcc_coeff.shape}')

    # Compute summary statistics across all frames
    mfcc_mean = np.mean(all_mfcc_coeffs, axis=0).tolist()  # Mean of each coefficient
    mfcc_std = np.std(all_mfcc_coeffs, axis=0).tolist()    # Std of each coefficient

    return {'mfcc_mean': mfcc_mean, 'mfcc_std': mfcc_std}


# transpose to have it in a better shape
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
@shared_task
def extract_basic_features(audio_path):
    # Check if the provided audio path exists and is a valid file
    if not os.path.isfile(audio_path):
        raise ValueError(f"Invalid audio path: {audio_path} does not exist or is not a file.")
    
    print(f'Processing audio file: {audio_path}')
    
    # Load audio
    audio = MonoLoader(filename=audio_path)()
    
    # Validate that audio is not None and is of correct type

   
    pitch_yin_fft = PitchYinFFT()(audio)
    envelope_shape=Envelope()(audio).tolist()
    
    # Return the extracted features
    return {
        "fundamental_frequency": {
            "pitch_yin_fft": pitch_yin_fft[0],  # tuple (pitch_yin_fft, pitch_confidence)
            "pitch_confidence": pitch_yin_fft[1]
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
        audio = MonoLoader(filename=audio_path)()
        w = Windowing(type='hann')
        spectrum = Spectrum()
        chromagram = Chromagram(numberBins=84, binsPerOctave=12)

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
    audio = MonoLoader(filename=audio_path)()
    envelope_shape=float(Envelope()(audio).mean())
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
    audio = MonoLoader(filename=audio_path)()

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