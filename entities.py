import re
import logging
from typing import List

logger = logging.getLogger(__name__)

def get_number(text):
    pattern = re.compile(r'\b\d{10,15}\b')
    return pattern.findall(text)

def get_email(text):
    r = re.compile(r'[A-Za-z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    return r.findall(str(text))

def get_name(text):
    # Simple heuristic: first line or first two words
    lines = text.strip().split('\n')
    if lines:
        words = lines[0].strip().split()
        if len(words) >= 2:
            return ' '.join(words[:2])
        elif words:
            return words[0]
    return "Name not found"

def get_skills(text, skills):
    # Simple keyword match
    found = set()
    for skill in skills:
        if skill.lower() in text.lower():
            found.add(skill)
    return found

def get_location(text):
    # Not implemented in minimal version
    return ["Location not found"]

def extract_education(text):
    # Not implemented in minimal version
    return []

def extract_experience_years(text):
    # Not implemented in minimal version
    return None
