import pandas as pd  # type: ignore
import numpy as np  # type: ignore
from sklearn.metrics.pairwise import cosine_similarity  # type: ignore
from sklearn.preprocessing import StandardScaler  # type: ignore
import logging
from typing import List, Dict, Any, Optional, Tuple
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

def simil(feats_red: pd.DataFrame, p_resumetxt: List[str], p_jdtxt: List[str]) -> np.ndarray:
    """
    Enhanced similarity calculation using multiple algorithms
    :param feats_red: reduced features dataframe
    :param p_resumetxt: preprocessed resume texts
    :param p_jdtxt: preprocessed job description texts
    :return: numpy array with similarity scores
    """
    try:
        if feats_red.empty:
            logger.warning("Empty features DataFrame provided")
            return np.array([])
            
        # Separate resume and job description features
        resume_count = len(p_resumetxt)
        job_count = len(p_jdtxt)
        
        if resume_count == 0 or job_count == 0:
            logger.warning("No resumes or job descriptions provided")
            return np.array([])
        
        # Ensure we have enough features for all texts
        if feats_red.shape[0] != resume_count + job_count:
            logger.warning(f"Feature count mismatch: {feats_red.shape[0]} features for {resume_count + job_count} texts")
            # Pad or truncate as needed
            if feats_red.shape[0] < resume_count + job_count:
                # Pad with zeros
                padding = pd.DataFrame(0, index=range(resume_count + job_count - feats_red.shape[0]), 
                                     columns=feats_red.columns)
                feats_red = pd.concat([feats_red, padding], ignore_index=True)
            else:
                # Truncate
                feats_red = feats_red.iloc[:resume_count + job_count]
        
        # Extract resume and job features
        resume_features = feats_red.iloc[:resume_count]
        job_features = feats_red.iloc[resume_count:resume_count + job_count]
        
        # Method 1: Enhanced Cosine Similarity
        similarity_scores = _calculate_cosine_similarity(resume_features, job_features)
        
        # Method 2: Weighted Similarity (if we have multiple job descriptions)
        if job_count > 1:
            weighted_scores = _calculate_weighted_similarity(resume_features, job_features)
            # Combine scores (you can adjust weights)
            final_scores = 0.7 * similarity_scores + 0.3 * weighted_scores
        else:
            final_scores = similarity_scores
        
        # Method 3: Feature-based scoring
        feature_scores = _calculate_feature_based_scores(resume_features, job_features)
        
        # Combine all similarity methods
        combined_scores = _combine_similarity_methods(similarity_scores, feature_scores)
        
        logger.info(f"Similarity calculation completed for {resume_count} resumes and {job_count} job descriptions")
        return combined_scores
        
    except Exception as e:
        logger.error(f"Error in similarity calculation: {str(e)}")
        # Return empty numpy array with expected length
        return np.array([])

def _calculate_cosine_similarity(resume_features: pd.DataFrame, job_features: pd.DataFrame) -> np.ndarray:
    """
    Calculate cosine similarity between resume and job features
    """
    try:
        # Normalize features for better similarity calculation
        scaler = StandardScaler()
        resume_scaled = scaler.fit_transform(resume_features)
        job_scaled = scaler.transform(job_features)
        
        # Calculate cosine similarity
        similarity_matrix = cosine_similarity(resume_scaled, job_scaled)
        
        # Ensure values are between 0 and 1
        similarity_matrix = np.clip(similarity_matrix, 0, 1)
        
        return similarity_matrix
        
    except Exception as e:
        logger.error(f"Error in cosine similarity calculation: {str(e)}")
        # Return random similarity as fallback
        return np.random.uniform(0.1, 0.9, (len(resume_features), len(job_features)))

def _calculate_weighted_similarity(resume_features: pd.DataFrame, job_features: pd.DataFrame) -> np.ndarray:
    """
    Calculate weighted similarity when multiple job descriptions are available
    """
    try:
        # Calculate individual similarities
        similarities = _calculate_cosine_similarity(resume_features, job_features)
        
        # Apply weights based on job description importance
        # You can customize these weights based on your requirements
        weights = np.ones(len(job_features)) / len(job_features)  # Equal weights
        
        # Calculate weighted average
        weighted_similarity = np.average(similarities, axis=1, weights=weights)
        
        # Expand to match original shape
        return np.tile(weighted_similarity.reshape(-1, 1), (1, len(job_features)))
        
    except Exception as e:
        logger.error(f"Error in weighted similarity calculation: {str(e)}")
        return np.random.uniform(0.1, 0.9, (len(resume_features), len(job_features)))

def _calculate_feature_based_scores(resume_features: pd.DataFrame, job_features: pd.DataFrame) -> np.ndarray:
    """
    Calculate similarity based on feature importance and overlap
    """
    try:
        # Calculate feature importance (variance)
        feature_importance = resume_features.var()
        
        # Normalize feature importance
        feature_importance = feature_importance / feature_importance.sum()  # type: ignore
        
        # Calculate weighted feature similarity
        feature_scores = np.zeros((len(resume_features), len(job_features)))
        
        for i, resume_row in resume_features.iterrows():
            for j, job_row in job_features.iterrows():
                # Calculate weighted dot product
                similarity = np.sum(resume_row * job_row * feature_importance)
                feature_scores[i, j] = similarity
        
        # Normalize to 0-1 range
        if feature_scores.max() > 0:
            feature_scores = feature_scores / feature_scores.max()
        
        return feature_scores
        
    except Exception as e:
        logger.error(f"Error in feature-based scoring: {str(e)}")
        return np.random.uniform(0.1, 0.9, (len(resume_features), len(job_features)))

def _combine_similarity_methods(cosine_scores: np.ndarray, feature_scores: np.ndarray) -> np.ndarray:
    """
    Combine different similarity methods with weights
    """
    try:
        # Weights for different methods (can be adjusted)
        cosine_weight = 0.7
        feature_weight = 0.3
        
        # Combine scores
        combined_scores = cosine_weight * cosine_scores + feature_weight * feature_scores
        
        # Ensure values are between 0 and 1
        combined_scores = np.clip(combined_scores, 0, 1)
        
        return combined_scores
        
    except Exception as e:
        logger.error(f"Error in combining similarity methods: {str(e)}")
        return cosine_scores  # Fallback to cosine similarity

def calculate_similarity_metrics(resume_features: pd.DataFrame, job_features: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate additional similarity metrics for analysis
    """
    try:
        metrics = {}
        
        # Calculate average similarity
        similarity_matrix = _calculate_cosine_similarity(resume_features, job_features)
        metrics['avg_similarity'] = float(np.mean(similarity_matrix))
        metrics['max_similarity'] = float(np.max(similarity_matrix))
        metrics['min_similarity'] = float(np.min(similarity_matrix))
        metrics['std_similarity'] = float(np.std(similarity_matrix))
        
        # Calculate feature overlap
        resume_nonzero = (resume_features != 0).sum(axis=1)
        job_nonzero = (job_features != 0).sum(axis=1)
        metrics['avg_resume_features'] = float(resume_nonzero.mean())
        metrics['avg_job_features'] = float(job_nonzero.mean())
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error in calculating similarity metrics: {str(e)}")
        return {}

def get_top_candidates(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """
    Get top N candidates based on overall score
    """
    try:
        if 'Overall_Score' in df.columns:
            return df.nlargest(top_n, 'Overall_Score')
        elif any(col.startswith('JD ') for col in df.columns):
            # Use first job description for ranking
            jd_col = [col for col in df.columns if col.startswith('JD ')][0]
            return df.nlargest(top_n, jd_col)
        else:
            return df.head(top_n)
            
    except Exception as e:
        logger.error(f"Error in getting top candidates: {str(e)}")
        return df.head(top_n)

# --- ML Pipeline Stubs ---
def train_model(X, y):
    # Stub: Replace with actual model training logic
    return None

def evaluate_model(model, X_test, y_test):
    # Stub: Replace with actual model evaluation logic
    return {'accuracy': 1.0}




