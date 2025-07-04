#!/usr/bin/env python3
"""
Resume Scorer - Quick Win #1
Rate resumes 1-10 based on job match with detailed scoring breakdown
"""

import re
from typing import Dict, List, Tuple, Any, Optional
from text_processing import preprocess
from entities import get_skills, get_name, get_email
import features
import model

class ResumeScorer:
    """Score resumes from 1-10 based on job requirements"""
    
    def __init__(self):
        self.scoring_weights = {
            'skills_match': 0.4,      # 40% weight
            'experience_level': 0.25,  # 25% weight
            'education': 0.15,         # 15% weight
            'contact_info': 0.1,       # 10% weight
            'overall_quality': 0.1     # 10% weight
        }
    
    def score_resume(self, resume_text: str, job_description: str, skills_list: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Score a resume from 1-10 based on job match
        
        Args:
            resume_text: Resume content
            job_description: Job requirements
            skills_list: List of skills to match against
            
        Returns:
            Dictionary with score and breakdown
        """
        try:
            # Initialize scores
            scores = {}
            
            # 1. Skills Match (40% weight)
            skills_score = self._calculate_skills_score(resume_text, job_description, skills_list)
            scores['skills_match'] = skills_score
            
            # 2. Experience Level (25% weight)
            experience_score = self._calculate_experience_score(resume_text, job_description)
            scores['experience_level'] = experience_score
            
            # 3. Education (15% weight)
            education_score = self._calculate_education_score(resume_text, job_description)
            scores['education'] = education_score
            
            # 4. Contact Information (10% weight)
            contact_score = self._calculate_contact_score(resume_text)
            scores['contact_info'] = contact_score
            
            # 5. Overall Quality (10% weight)
            quality_score = self._calculate_quality_score(resume_text)
            scores['overall_quality'] = quality_score
            
            # 6. Similarity Score (not included in weighted final score yet)
            similarity_score = self._calculate_similarity_score(resume_text, job_description)
            scores['similarity_score'] = similarity_score
            
            # Calculate weighted final score
            final_score = self._calculate_weighted_score(scores)
            
            # Get score description
            score_description = self._get_score_description(final_score)
            
            return {
                'final_score': round(final_score, 1),
                'score_description': score_description,
                'breakdown': scores,
                'weights': self.scoring_weights,
                'recommendations': self._get_recommendations(scores, resume_text, job_description)
            }
            
        except Exception as e:
            return {
                'final_score': 0,
                'score_description': 'Error in scoring',
                'error': str(e),
                'breakdown': {},
                'weights': self.scoring_weights,
                'recommendations': ['Error occurred during scoring']
            }
    
    def _calculate_skills_score(self, resume_text: str, job_description: str, skills_list: Optional[List[str]] = None) -> float:
        """Calculate skills match score (0-10)"""
        try:
            # Extract skills from resume
            if skills_list is None:
                skills_list = self._get_default_skills()
            
            resume_skills = get_skills(resume_text, skills_list)
            
            # Extract skills from job description
            job_skills = get_skills(job_description, skills_list)
            
            if not job_skills:
                return 5.0  # Neutral score if no skills in job description
            
            # Calculate match percentage
            matched_skills = set(resume_skills).intersection(set(job_skills))
            match_percentage = len(matched_skills) / len(job_skills)
            
            # Convert to 0-10 scale
            score = match_percentage * 10
            
            return min(score, 10.0)
            
        except Exception:
            return 5.0
    
    def _calculate_experience_score(self, resume_text: str, job_description: str) -> float:
        """Calculate experience level score (0-10)"""
        try:
            # Look for experience keywords in job description
            experience_keywords = ['years', 'experience', 'senior', 'junior', 'entry', 'level']
            job_has_experience_req = any(keyword in job_description.lower() for keyword in experience_keywords)
            
            if not job_has_experience_req:
                return 7.0  # Neutral score if no experience requirements
            
            # Extract years of experience from resume
            experience_patterns = [
                r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?experience',
                r'(\d+)\s*(?:years?|yrs?)\s*(?:in\s*)?(?:the\s*)?(?:field|industry)',
                r'experience.*?(\d+)\s*(?:years?|yrs?)',
            ]
            
            years_experience = 0
            for pattern in experience_patterns:
                matches = re.findall(pattern, resume_text.lower())
                if matches:
                    years_experience = max(years_experience, int(matches[0]))
                    break
            
            # Score based on experience level
            if years_experience >= 5:
                return 9.0
            elif years_experience >= 3:
                return 7.5
            elif years_experience >= 1:
                return 6.0
            else:
                return 4.0
                
        except Exception:
            return 5.0
    
    def _calculate_education_score(self, resume_text: str, job_description: str) -> float:
        """Calculate education score (0-10)"""
        try:
            # Look for education keywords
            education_keywords = ['bachelor', 'master', 'phd', 'degree', 'university', 'college']
            
            resume_education = any(keyword in resume_text.lower() for keyword in education_keywords)
            job_requires_education = any(keyword in job_description.lower() for keyword in education_keywords)
            
            if not job_requires_education:
                return 7.0  # Neutral score if no education requirements
            
            if resume_education:
                # Check for advanced degrees
                if any(degree in resume_text.lower() for degree in ['phd', 'doctorate']):
                    return 10.0
                elif any(degree in resume_text.lower() for degree in ['master', 'mba']):
                    return 9.0
                elif any(degree in resume_text.lower() for degree in ['bachelor', 'b.s.', 'b.a.']):
                    return 8.0
                else:
                    return 6.0
            else:
                return 3.0
                
        except Exception:
            return 5.0
    
    def _calculate_contact_score(self, resume_text: str) -> float:
        """Calculate contact information completeness score (0-10)"""
        try:
            score = 0
            
            # Check for name
            name = get_name(resume_text)
            if name:
                score += 2
            
            # Check for email
            email = get_email(resume_text)
            if email:
                score += 3
            
            # Check for phone
            phone_pattern = r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
            if re.search(phone_pattern, resume_text):
                score += 2
            
            # Check for location
            location_patterns = [
                r'\b[A-Z][a-z]+,\s*[A-Z]{2}\b',  # City, State
                r'\b[A-Z][a-z]+,\s*[A-Z][a-z]+\b',  # City, Country
            ]
            has_location = any(re.search(pattern, resume_text) for pattern in location_patterns)
            if has_location:
                score += 2
            
            # Check for LinkedIn/GitHub
            social_patterns = [
                r'linkedin\.com',
                r'github\.com',
                r'portfolio',
            ]
            has_social = any(re.search(pattern, resume_text.lower()) for pattern in social_patterns)
            if has_social:
                score += 1
            
            return min(score, 10.0)
            
        except Exception:
            return 5.0
    
    def _calculate_quality_score(self, resume_text: str) -> float:
        """Calculate overall resume quality score (0-10)"""
        try:
            score = 5.0  # Start with neutral score
            
            # Check length (not too short, not too long)
            word_count = len(resume_text.split())
            if 100 <= word_count <= 500:
                score += 1
            elif word_count > 500:
                score += 0.5
            
            # Check for professional formatting
            has_sections = any(section in resume_text.lower() for section in ['experience', 'education', 'skills'])
            if has_sections:
                score += 1
            
            # Check for action verbs
            action_verbs = ['developed', 'implemented', 'managed', 'led', 'created', 'designed', 'built']
            has_action_verbs = any(verb in resume_text.lower() for verb in action_verbs)
            if has_action_verbs:
                score += 1
            
            # Check for metrics/numbers
            has_metrics = bool(re.search(r'\d+%|\d+\s*(?:users|customers|projects)', resume_text.lower()))
            if has_metrics:
                score += 1
            
            # Check for technical keywords
            tech_keywords = ['python', 'javascript', 'react', 'aws', 'docker', 'sql', 'api']
            tech_count = sum(1 for keyword in tech_keywords if keyword in resume_text.lower())
            if tech_count >= 3:
                score += 1
            
            return min(score, 10.0)
            
        except Exception:
            return 5.0
    
    def _calculate_weighted_score(self, scores: Dict[str, float]) -> float:
        """Calculate weighted final score"""
        try:
            weighted_sum = 0
            for category, score in scores.items():
                weight = self.scoring_weights.get(category, 0)
                weighted_sum += score * weight
            
            return weighted_sum
            
        except Exception:
            return 5.0
    
    def _get_score_description(self, score: float) -> str:
        """Get human-readable score description"""
        if score >= 9.0:
            return "Excellent Match - Highly Recommended"
        elif score >= 7.5:
            return "Very Good Match - Strong Candidate"
        elif score >= 6.0:
            return "Good Match - Worth Considering"
        elif score >= 4.5:
            return "Fair Match - May Need Training"
        elif score >= 3.0:
            return "Poor Match - Not Recommended"
        else:
            return "Very Poor Match - Avoid"
    
    def _get_recommendations(self, scores: Dict[str, float], resume_text: str, job_description: str) -> List[str]:
        """Get improvement recommendations based on scores"""
        recommendations = []
        
        if scores.get('skills_match', 0) < 6.0:
            recommendations.append("Add more relevant skills to match job requirements")
        
        if scores.get('experience_level', 0) < 6.0:
            recommendations.append("Highlight relevant work experience more prominently")
        
        if scores.get('education', 0) < 6.0:
            recommendations.append("Consider adding relevant education or certifications")
        
        if scores.get('contact_info', 0) < 6.0:
            recommendations.append("Add complete contact information (email, phone, location)")
        
        if scores.get('overall_quality', 0) < 6.0:
            recommendations.append("Improve resume formatting and add specific achievements")
        
        if not recommendations:
            recommendations.append("Resume looks good! Consider adding more specific achievements")
        
        return recommendations
    
    def _get_default_skills(self) -> List[str]:
        """Get default skills list for matching"""
        return [
            "python", "javascript", "java", "react", "node.js", "sql", "aws", "docker",
            "machine learning", "data science", "web development", "mobile development",
            "devops", "agile", "scrum", "git", "api", "microservices", "cloud computing"
        ]
    
    def _calculate_similarity_score(self, resume_text: str, job_description: str) -> float:
        """Calculate similarity score between resume and job description using feature-based similarity (0-10)"""
        try:
            # Preprocess texts (returns list, so get first element)
            resume_processed = preprocess([resume_text])[0]
            jd_processed = preprocess([job_description])[0]
            # Extract features
            feats_df = features.txt_features([resume_processed], [jd_processed])
            feats_red = features.feats_reduce(feats_df)
            # Calculate similarity
            sim_scores = model.simil(feats_red, [resume_processed], [jd_processed])
            if sim_scores.size > 0:
                # sim_scores is a matrix, take the first value
                sim_score = sim_scores[0][0]
                # Scale to 0-10
                return round(sim_score * 10, 2)
            else:
                return 5.0
        except Exception:
            return 5.0

# Global instance for easy access
resume_scorer = ResumeScorer() 