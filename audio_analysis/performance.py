import numpy as np
from scipy.spatial.distance import cosine
from sklearn.metrics import r2_score
from dtaidistance import dtw


class EvaluatePerformanceClass:
    def compute_feature_scores(self,ref_data,uploaded_data):
        """Computes similarity scores for each feature between reference and uploaded audio."""
        ref_extracted_data = self.extract_features(ref_data)
        uploaded_extracted_data = self.extract_features(uploaded_data)

        # Calculate similarity for each feature type.
        scores = {}
        scores['pitch_yin_fft'] = self.r2_similarity(
            ref_extracted_data['pitch_yin_fft'], uploaded_extracted_data['pitch_yin_fft']
        )
        scores['pitch_confidence'] = self.r2_similarity(
            ref_extracted_data['pitch_confidence'], uploaded_extracted_data['pitch_confidence']
        )
        scores['chroma'] = self.compare_arrays(
            ref_extracted_data['chroma'], uploaded_extracted_data['chroma']
        )
        '''
        scores['envelope_shape'] = self.compare_arrays(
            ref_extracted_data['envelope_shape'], uploaded_extracted_data['envelope_shape']
        )'''
        scores['avg_harmonic_ratio'] = self.compare_features(
            ref_extracted_data['avg_harmonic_ratio'], uploaded_extracted_data['avg_harmonic_ratio']
        )
        scores['mfcc_mean'] = self.compare_arrays(
            ref_extracted_data['mfcc_mean'], uploaded_extracted_data['mfcc_mean']
        )
        scores['mfcc_std'] = self.compare_arrays(
            ref_extracted_data['mfcc_std'], uploaded_extracted_data['mfcc_std']
        )
        scores['integrated_loudness'] = self.compare_features(
            ref_extracted_data['integrated_loudness'], uploaded_extracted_data['integrated_loudness']
        )
        scores['dynamic_range'] = self.compare_features(
            ref_extracted_data['dynamic_range'], uploaded_extracted_data['dynamic_range']
        )
        scores['tempo'] = self.compare_features(
            ref_extracted_data['tempo'], uploaded_extracted_data['tempo']
        )
        scores['beat_positions'] = self.compare_arrays(
            ref_extracted_data['beat_positions'], uploaded_extracted_data['beat_positions']
        )
        
        scores['zcr_mean']=self.compare_features(
            ref_extracted_data['zcr_mean'],uploaded_extracted_data['zcr_mean']
        )

        scores['zcr_std']=self.compare_features(
            ref_extracted_data['zcr_std'], uploaded_extracted_data['zcr_std']
        )
        scores['spectral_contrast_mean']=self.compare_arrays(
            ref_extracted_data['spectral_contrast_mean'], uploaded_extracted_data['spectral_contrast_mean']
        )

        scores['spectral_contrast_std']=self.compare_arrays(
            ref_extracted_data['spectral_contrast_std'],uploaded_extracted_data['spectral_contrast_std']
        )

        reference_key=ref_extracted_data['key']
        reference_scale=ref_extracted_data['scale']

        uploaded_key = uploaded_extracted_data['key']
        uploaded_scale = uploaded_extracted_data['scale']

        keys = {'ref_key': reference_key, 'uploaded_key': uploaded_key}
        scales = {'ref_scale': reference_scale, 'uploaded_scale': uploaded_scale}

        return scores,keys,scales
        


    
    def extract_features(self,data):
        features = {
                "pitch_yin_fft": data["basic_features"]["fundamental_frequency"]["pitch_yin_fft"],
                "pitch_confidence": data["basic_features"]["fundamental_frequency"]["pitch_confidence"],
                "chroma": data["chroma_features"]["chroma"],
                "envelope_shape": data["envelope_shape"],
                "avg_harmonic_ratio": data["avg_harmonic_ratio"],
                "mfcc_mean": data["mfcc"]["mfcc_mean"],
                "mfcc_std": data["mfcc"]["mfcc_std"],
                "integrated_loudness": data["loudness_features"]["Integrated_loudness"],
                "dynamic_range": data["loudness_features"]["Dynamic_range"],
                "tempo": data["tempo_and_beat_positions"]["tempo"],
                "beat_positions": data["tempo_and_beat_positions"]["beat_postions"],
                "spectral_complexity":data["spectral_complexity"],
                "zcr_mean":data["zero_crossing_rate"]["zcr_mean"],
                "zcr_std":data["zero_crossing_rate"]["zcr_std"],
                "spectral_contrast_mean":data["spectral_contrast"]["contrast_mean"],
                "spectral_contrast_std":data["spectral_contrast"]["contrast_std"],
                "dynamic_complexity":data["dynamic_complexity"],
                "key":data["key_and_scale"]["key"],
                "scale":data["key_and_scale"]["scale"],


            }
        return features
    
    def r2_similarity(self, vector1, vector2):
        """Computes the R² score between two vectors."""
        if len(vector1) == len(vector2):
            return r2_score(vector1, vector2)
        else:
            # Pad the shorter vector with zeros
            max_len = max(len(vector1), len(vector2))
            vector1 = np.pad(vector1, (0, max_len - len(vector1)), 'constant')
            vector2 = np.pad(vector2, (0, max_len - len(vector2)), 'constant')
            return r2_score(vector1, vector2)
            

    def cosine_similarity(self, vector1, vector2):
        """Computes the cosine similarity between two vectors."""
        if len(vector1) == len(vector2):
            return 1 - cosine(vector1, vector2)
        else:
            # Pad the shorter vector with zeros
            max_len = max(len(vector1), len(vector2))
            vector1 = np.pad(vector1, (0, max_len - len(vector1)), 'constant')
            vector2 = np.pad(vector2, (0, max_len - len(vector2)), 'constant')
            return 1 - cosine(vector1, vector2)
 
    def compare_features(self,feature_ref, feature_new):
        """Compares two scalar features using a normalized difference."""
        return 1 - abs(feature_ref - feature_new) / (abs(feature_ref) + abs(feature_new) + 1e-9)
    
    def dtwdistance_complement(self,array1,array2):
        distance = dtw.distance(array1,array2)
        return 1-distance

    def compare_arrays(self,array1, array2):
        """Compares two arrays using cosine similarity."""
        return self.dtwdistance_complement(np.array(array1), np.array(array2))
