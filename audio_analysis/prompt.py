
def analyse_sound(query_audio_features):
    return f"""
        Given the following  extracted features extracted from an audio: {query_audio_features}
        Can you analyze the type of instrument used, the genre and possibly the genre and vocal style

        """
def noise_prompt(ref_audio_features,query_audio_features):
    return f'''
            You are an AI music evaluator that compares two tracks, a reference track and a query track, based on their extracted audio features. Your task is to grade the query track on its similarity to the reference track for each feature and provide an overall evaluation. Additionally, if the query track contains noise or lacks meaningful comparison to the reference track, make a note of this.
            Inputs:
            Reference Track Features: {ref_audio_features}
            Query Track Features: {query_audio_features}
            Task:
            For each feature:
            Grade the query track from 0 to 10 on how closely it matches the reference track for that feature.
            Explain the score briefly (e.g., "Tempo matches within 2 BPM, so the score is 9/10").
            Provide an overall similarity grade based on the weighted importance of each feature.
            Check for noise:
            If the query track's features deviate significantly from the reference across all criteria or show irregular patterns, identify it as noise.
            Provide a comment (e.g., "The query track appears to be noise as the features deviate significantly with no recognizable pattern").
            Output Format:
            Feature-by-Feature Analysis: [Include feature name, score, and explanation]
            Overall Similarity Grade: [Score out of 100 with reasoning]
            Noise Analysis: [State whether the track is noise and why]
            Please note if it is Noise should automatically assign a score of zero
            Return the analysis in JSON format:
            {{
                "score": <LLM_Generated_Score>,
                "reasoning": "<LLM_Recommendation>"
            }} '''




def newest_prompt(ref_audio_features,query_audio_features):
    return f"""
    "Please act as a music teacher with over 20 years of experience. 
    Given the following audio feature sets, assess how well the 'query' music performs in comparison to 
    the 'reference' music. The features for each piece are provided below. Please analyze the similarities 
    and differences in these features to determine a score that reflects the performance of the query music in terms of alignment, rhythm, melody, pitch, and timbre, 
    among other relevant aspects. The score should range from 0 to 100, 
    where 100 represents a perfect match with the reference music and 0 represents no alignment.

    Reference Audio Features: {ref_audio_features}

    Query Audio Features: {query_audio_features}
    Provide constructive feedback:  
    - Identify strengths and areas needing improvement.
    - Offer actionable advice to enhance the user’s performance.
    I would like the guidance to refleect deep expertise and practical knowledge in teaching music. 


     Assign a final performance grade (Range: 0 to 100, where 100 is perfect). You should this critically evaluating the users performance in all the features above 
    and holistically provide an accurate assessment of the user's performance.
    ### Output Format:
    Return the analysis in JSON format:
    {{
        "score": <LLM_Generated_Score>,
        "recommendation": "<LLM_Recommendation>"
    }}
    ### Recommendation Requirements:
    - Should be limited to 50 words and presented in a single paragraph.
    """



def new_prompt(ref_audio_features,query_audio_features):
    return f"""
    "Given the following audio feature sets, assess how well the 'query' music performs in comparison to 
    the 'reference' music. The features for each piece are provided below. Please analyze the similarities 
    and differences in these features to determine a score that reflects the performance of the query music in terms of alignment, rhythm, melody, pitch, and timbre, 
    among other relevant aspects. The score should range from 0 to 100, 
    where 100 represents a perfect match with the reference music and 0 represents no alignment.

    Reference Audio Features: {ref_audio_features}

    Query Audio Features: {query_audio_features}
    *Provide constructive feedback:*  
    - Identify strengths and areas needing improvement.
    - Offer actionable advice to enhance the user’s performance.


     *Assign a final performance grade* (Range: 0 to 100, where 100 is perfect). You should this critically evaluating the users performance in all the features above 
    and holistically provide an accurate assessment of the user's performance.
    ### Output Format:
    Return the analysis in *JSON* format:
    {{
        "score": <LLM_Generated_Score>,
        "recommendation": "<LLM_Recommendation>"
    }}

    ### Recommendation Requirements:
    - Should be limited to *50 words* and presented in a single paragraph.
    """


def initial_prompt(scores,keys,scales):
    return f"""
    Analyze the user’s performance based on the following scores, extracted from a comparison between a reference audio and the user’s audio. Your task is to *prioritize critical dimensions* such as *Pitch* and *Expression* over other aspects like tempo or loudness. Songs that may match in loudness and tempo but have poor pitch or harmonic control should be penalized more severely to ensure accurate scoring.

    ### Scoring Metrics and Ranges:
    - *Pitch (Accuracy and Stability):*  
    > *Most Critical Feature* – Misalignment here should significantly reduce the final score.
    - *Pitch Accuracy (Yin FFT)*: Scalar comparison (Range: 0 to 1; 1 is a perfect match).
        Score: {scores['pitch_yin_fft']}
    - *Pitch Confidence*: Scalar comparison (Range: 0 to 1; higher is better).
        Score: {scores['pitch_confidence']}

    - *Rhythm (Timing and Consistency):*
    - *Tempo Accuracy*: Scalar comparison (Range: 0 to 1; 1 is a perfect tempo match).  
        *Lower weight:* Minor discrepancies should not heavily impact the score.  
        Score: {scores['tempo']}
    - *Beat Position Matching*: DTW distance (Range: 0 to 1; lower indicates better alignment).  
        Score: {scores['beat_positions']}

    - *Dynamics (Volume and Intensity Control):*
    - *Integrated Loudness*: Absolute error difference (Ideal < 2 LUFS; lower is better).
        Score: {scores['integrated_loudness']}
    - *Dynamic Range*: Absolute error difference (Range: 0-20; lower is better).  
        *Loudness alignment alone* should not result in high scores unless accompanied by good pitch and expression.
        Score: {scores['dynamic_range']}

    - *Expression (Harmonic and Timbre Control):*
    > *Critical Feature* – Low scores here should significantly reduce the overall grade.
    - *Harmonic Ratio*: Scalar comparison (Range: 0 to 1; higher indicates better harmonic alignment).
        Score: {scores['avg_harmonic_ratio']}
    - *Chroma Similarity*: DTW distance (Range: 0 to 1; lower indicates better chromatic match).
        Score: {scores['chroma']}
    - *MFCC Mean Comparison*: DTW distance (Range: 0 to 1; lower is better).
        Score: {scores['mfcc_mean']}
    - *MFCC Std Comparison*: DTW distance (Range: 0 to 1; lower is better).  
        Score: {scores['mfcc_std']}
    - *Zero Crossing Rate Mean*: Scalar comparison (Range: 0 to 1; higher is better).
        Score: {scores['zcr_mean']}
    - *Zero Crossing Rate Std*: Scalar comparison (Range: 0 to 1; higher is better).
        Score: {scores['zcr_std']}
    - *Spectral Contrast Mean*: DTW distance (Range: 0 to 1; lower is better).
        Score: {scores['spectral_contrast_mean']}
    - *Spectral Contrast Std*: DTW distance (Range: 0 to 1; lower is better).
        Score: {scores['spectral_contrast_std']}

    - *Key and Scale:* 
    > These features cannot be directly compared numerically but are essential for understanding the harmonic context of the performance. 
    - *Key*: {keys['ref_key']} (Uploaded: {keys['uploaded_key']}) 
    - *Scale*: {scales['ref_scale']} (Uploaded: {scales['uploaded_scale']}) 
    > Consider how well the user’s performance aligns with the reference in terms of key and scale, and provide feedback on harmonic compatibility.

    ### Task:
    1. *Analyze the performance*

    2. *Provide constructive feedback:*  
    - Identify strengths and areas needing improvement.
    - Offer actionable advice to enhance the user’s performance.


    3. *Assign a final performance grade* (Range: 0 to 100, where 100 is perfect). You should this critically evaluating the users performance in all the features above 
    and holistically provide an accurate assessment of the user's performance.
    ### Output Format:
    Return the analysis in *JSON* format:
    {{
        "score": <LLM_Generated_Score>,
        "recommendation": "<LLM_Recommendation>"
    }}

    ### Recommendation Requirements:
    - Should be limited to *50 words* and presented in a single paragraph.
    """


def generate_prompt(scores, keys, scales): 
    """Creates a prompt for the LLM to analyze the user's performance based on rhythm, pitch, dynamics, and expression."""
    return f"""
                Analyze the user’s performance based on the scores extracted from a comparison between a reference audio and the user’s audio. 
                Focus on three main criteria: Pitch, Rhythm, and Expression. Each feature’s contribution should reflect its importance to the overall musical quality, with pitch weighted highest, followed by rhythm, and then expression. The features are compared using mainly Dynamic Time Warping and Scalar Comparison.

                For Dynamic Time Warping, the range of values is from negative infinity to 1, with 1 indicating a perfect match. Higher values indicate better performance, while lower values suggest greater divergence from the reference song.

                For scalar comparison, the values range from 0 to 1, with 1 indicating a perfect match and lower values indicating poorer alignment.

                Taking these two criteria, assess the user’s performance based on the following scoring metrics:

                Weighted Scoring Metrics and Ranges:
                Pitch (Accuracy and Stability):

                Primary Factor (25% of Total Score) – Pitch accuracy and stability should make up half of the total score. Any misalignment here should heavily impact the final score.

                Pitch Accuracy (Yin FFT): Scalar comparison (Range: 0 to 1; 1 is a perfect match). Contributes 25% of the total score.
                Score: {scores.get('pitch_yin_fft', 'N/A')}
                Rhythm (Timing and Consistency):

                Secondary Factor (35% of Total Score) – Rhythm accuracy should account for 35% of the total score, with misalignment in beat positions or tempo impacting the score proportionally.

                Tempo Accuracy: Scalar comparison (Range: 0 to infinity; 1 is a perfect tempo match). Contributes 10% of the total score.
                Score: {scores.get('tempo', 'N/A')}
                Beat Position Matching: DTW distance complement (Range: negative infinity to 1; higher indicates better alignment). Contributes 25% of the total score.
                Score: {scores.get('beat_positions', 'N/A')}
                Expression (Harmonic and Timbre Control):

                Tertiary Factor (30% of Total Score) – Expression factors should constitute 30% of the total score. This criterion includes harmonic alignment, chromatic similarity, and timbre.

                Harmonic Ratio: Scalar comparison (Range: 0 to 1; higher indicates better harmonic alignment). Contributes 8% of the total score.
                Score: {scores.get('avg_harmonic_ratio', 'N/A')}
                Chroma Similarity: DTW distance complement (Range: negative infinity to 1; higher indicates better chromatic match). Contributes 12% of the total score.
                Score: {scores.get('chroma', 'N/A')}
                MFCC Mean Comparison: DTW distance complement (Range: negative infinity to 1; higher is better). Contributes 10% of the total score.
                Score: {scores.get('mfcc_mean', 'N/A')}
                Additional Metrics (Minimal Weight): 
                These features should minimally impact the final score unless there is a severe discrepancy. So the total score
                should account for 
                Score: {scores.get('integrated_loudness', 'N/A')} (1% of total score)
                Dynamic Range: Scalar comparison (Range: 0-1; lower is better). 
                Score: {scores.get('dynamic_range', 'N/A')}(1% of total score)
                Zero Crossing Rate Mean and Std: Scalar comparison (Range: 0 to 1; higher is better).
                Scores: {scores.get('zcr_mean', 'N/A')}, {scores.get('zcr_std', 'N/A')} (1% of total score)
                Spectral Contrast Mean and Std: DTW distance complement (Range: negative infinity to 1; higher is better).
                Scores: {scores.get('spectral_contrast_mean', 'N/A')}, {scores.get('spectral_contrast_std', 'N/A')}
                Key and Scale: (3% of total score)
                These contribute to harmonic compatibility but do not require a direct numerical comparison. A mismatch in key or scale should reduce the final score by a significant margin, impacting the expression category.

                Key: {keys.get('ref_key', 'N/A')} (Uploaded: {keys.get('uploaded_key', 'N/A')})
                Scale: {scales.get('ref_scale', 'N/A')} (Uploaded: {scales.get('uploaded_scale', 'N/A')}) (3% of total score)

                Task:
                Analyze the Performance:

                Evaluate the user’s performance across the primary features, weighting Pitch (25%), Rhythm (35%),Expression (30%) and Additional metrics.
                Penalize heavily for major misalignments in pitch, rhythm, and expression, especially where features deviate strongly from the reference.
                Provide Constructive Feedback:

                Identify strengths and areas needing improvement.
                Offer actionable advice to enhance the user’s performance.
                Assign a Final Performance Grade
                Calculate a score from 0 to 100, factoring in each weighted component.
                Consider overall consistency and alignment in pitch, rhythm, and expression when giving the final assessment.
                Output Format:
                Return the analysis in JSON format:
                {{
                    "score": <LLM_Generated_Score>,
                    "recommendation": "<LLM_Recommendation>"
                }}
                Recommendation Requirements:
                Limit the recommendation to 50 words in a single paragraph, 
                summarizing key points for improvement based on the above features
                
                """
