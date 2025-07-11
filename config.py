import os

class Config:
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 10 * 1024 * 1024))  # 10MB default
    SUPPORTED_FORMATS = ['.pdf', '.docx']
    SCORE_WEIGHTS = {
        'skills_match': 0.3,
        'experience_level': 0.25,
        'education': 0.15,
        'contact_info': 0.1,
        'overall_quality': 0.2
    } 