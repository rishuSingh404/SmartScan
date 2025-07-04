import re
import nltk
import os
import logging

logger = logging.getLogger(__name__)

def setup_nltk():
    """Setup NLTK data once during initialization"""
    try:
        nltk_data_path = os.path.join(os.path.dirname(__file__), 'nltk_data')
        
        if not os.path.exists(nltk_data_path):
            os.makedirs(nltk_data_path)
        
        # Download required NLTK data
        required_packages = [
            'stopwords',
            'punkt',
            'averaged_perceptron_tagger',
            'wordnet',
            'omw-1.4'
        ]
        
        for package in required_packages:
            try:
                nltk.download(package, download_dir=nltk_data_path, quiet=True)
            except Exception as e:
                logger.warning(f"Could not download {package}: {e}")
    except Exception as e:
        logger.error(f"Error setting up NLTK: {e}")

# Call setup once at module import
setup_nltk()

from nltk.corpus import stopwords

def preprocess(txt):
    """
    This function returns a preprocessed list of texts 
    :param txt: list containing texts
    :return: preprocessed list of texts
    """
    try:
        sw = set(stopwords.words('english'))  # Use set for O(1) lookup
        p_txt = []

        for resume in txt:
            # Combine regex operations for efficiency
            text = re.sub(r'\s+', ' ', resume)  # Remove extra spaces
            text = re.sub(r'[^a-zA-Z\s]', ' ', text)  # Keep only letters and spaces
            text = text.lower().strip()
            
            # Tokenize and filter in one pass
            words = [word for word in text.split() 
                    if word.isalpha() and word not in sw and len(word) > 1]
            
            p_txt.append(" ".join(words))

        return p_txt
    except Exception as e:
        logger.error(f"Error in preprocessing: {str(e)}")
        return txt  # Return original text if preprocessing fails
