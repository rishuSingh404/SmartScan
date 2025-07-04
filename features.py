import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import logging
from typing import List, Union, Optional
import numpy as np

logger = logging.getLogger(__name__)

def txt_features(p_resumetxt: List[str], p_jdtxt: List[str]) -> pd.DataFrame:
    """
    This function returns a dataframe of features 
    extracted from a list of texts using transformers if available,
    otherwise falls back to TF-IDF.
    :param p_resumetxt: preprocessed list of resume texts
    :param p_jdtxt: preprocessed list of job description texts
    :return: dataframe of features 
    """
    try:
        txt = p_resumetxt + p_jdtxt
        if not txt:
            logger.warning("Empty text list provided")
            return pd.DataFrame()
        # Only use TF-IDF
        tv = TfidfVectorizer(max_df=0.85, min_df=1, ngram_range=(1,3))
        tfidf_wm = tv.fit_transform(txt)
        tfidf_tokens = tv.get_feature_names_out()
        tfidf_array = tfidf_wm.toarray()  # type: ignore
        df_tfidfvect = pd.DataFrame(data=tfidf_array, columns=tfidf_tokens)
        return df_tfidfvect
    except Exception as e:
        logger.error(f"Error in txt_features: {str(e)}")
        return pd.DataFrame()

def feats_reduce(feats_df: pd.DataFrame) -> pd.DataFrame:
    """
    This function returns a reduced dimensionality of a dataframe of features
    :param feats_df: dataframe of features extracted from a list of texts
    :return: reduced dimensionality of a dataframe of features
    """
    try:
        if feats_df.empty:
            logger.warning("Empty features DataFrame provided")
            return pd.DataFrame()
            
        # Ensure we have enough features for dimensionality reduction
        if feats_df.shape[1] <= 30:
            logger.info("Features already have <= 30 dimensions, returning as is")
            return feats_df
            
        dimrec = TruncatedSVD(n_components=30, n_iter=7, random_state=42)
        feats_red = dimrec.fit_transform(feats_df)
        
        # Converting transformed vector to DataFrame
        feat_red = pd.DataFrame(feats_red)
        return feat_red
        
    except Exception as e:
        logger.error(f"Error in feats_reduce: {str(e)}")
        # Return original DataFrame as fallback
        return feats_df

