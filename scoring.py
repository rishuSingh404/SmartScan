import re
import csv
from typing import List, Dict, Any, Optional
try:
    import spacy  # type: ignore
    nlp = spacy.load('en_core_web_sm')
    SPACY_AVAILABLE = True
except Exception:
    SPACY_AVAILABLE = False
try:
    from sentence_transformers import SentenceTransformer, util  # type: ignore
    st_model = SentenceTransformer('all-MiniLM-L6-v2')
    ST_AVAILABLE = True
except Exception:
    ST_AVAILABLE = False

class ResumeScorer:
    def __init__(self):
        self.skills_set = self.load_skills('Data/skill_red.csv')

    def load_skills(self, filepath: str) -> set:
        skills = set()
        with open(filepath, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                if row:
                    skills.add(row[0].strip().lower())
        return skills

    def extract_skills(self, text: str) -> set:
        extracted_skills = set()
        for skill in self.skills_set:
            pattern = r'\b' + skill.replace('-', r'[ \-]?') + r'\b'
            if re.search(pattern, text.lower()):
                extracted_skills.add(skill)
        return extracted_skills

    def extract_keywords(self, text: str) -> set:
        if SPACY_AVAILABLE:
            doc = nlp(text)
            return set([token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct and len(token) > 3])
        else:
            return set(w for w in re.findall(r'\b\w{4,}\b', text.lower()))

    def extract_experience(self, text: str) -> int:
        if SPACY_AVAILABLE:
            doc = nlp(text)
            years = [ent.text for ent in doc.ents if ent.label_ == 'DATE']
            # Try to extract years from date entities
            years_found = re.findall(r'(\d{4})', ' '.join(years))
            if years_found:
                years_found = [int(y) for y in years_found]
                if len(years_found) >= 2:
                    return max(years_found) - min(years_found)
        # fallback to regex
        years = re.findall(r'(\d+)\s+years?', text.lower())
        if years:
            return max(int(y) for y in years)
        years_mentioned = re.findall(r'(19\d{2}|20\d{2})', text)
        if years_mentioned:
            years_mentioned = [int(y) for y in years_mentioned]
            if years_mentioned:
                return max(years_mentioned) - min(years_mentioned)
        return 0

    def extract_education(self, text: str) -> str:
        degrees = ['phd', 'doctor', 'master', 'msc', 'm.tech', 'mba', 'bachelor', 'bsc', 'b.tech', 'ba', 'be', 'bs']
        if SPACY_AVAILABLE:
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ == 'EDUCATION' or any(degree in ent.text.lower() for degree in degrees):
                    return ent.text.lower()
        for degree in degrees:
            if degree in text.lower():
                return degree
        return ''

    def extract_contact_info(self, text: str) -> Dict[str, bool]:
        email = bool(re.search(r'[\w\.-]+@[\w\.-]+', text))
        phone = bool(re.search(r'\b\d{10,}\b', text))
        linkedin = bool(re.search(r'linkedin\.com', text.lower()))
        return {'email': email, 'phone': phone, 'linkedin': linkedin}

    def semantic_similarity(self, resume_text: str, jd_text: str) -> float:
        if ST_AVAILABLE:
            try:
                resume_emb = st_model.encode(resume_text, convert_to_tensor=True)
                jd_emb = st_model.encode(jd_text, convert_to_tensor=True)
                similarity = util.pytorch_cos_sim(resume_emb, jd_emb).item()
                return similarity
            except Exception:
                return 0.0
        return 0.0

    def score_resume(self, resume_text: str, job_description: str, skills_list: Optional[List[str]] = None) -> Dict[str, Any]:
        # Skills Match (40)
        resume_skills = self.extract_skills(resume_text)
        jd_skills = self.extract_skills(job_description)
        matched_skills = resume_skills & jd_skills
        skills_score = (len(matched_skills) / max(1, len(jd_skills))) * 35 if jd_skills else 0

        # Keyword Density (15)
        jd_keywords = self.extract_keywords(job_description)
        resume_keywords = self.extract_keywords(resume_text)
        matched_keywords = resume_keywords & jd_keywords
        keyword_score = (len(matched_keywords) / max(1, len(jd_keywords))) * 15 if jd_keywords else 0

        # Experience (15)
        resume_exp = self.extract_experience(resume_text)
        jd_exp = self.extract_experience(job_description)
        if jd_exp > 0:
            if resume_exp >= jd_exp:
                exp_score = 15
            elif resume_exp > 0:
                exp_score = 8
            else:
                exp_score = 0
        else:
            exp_score = 8 if resume_exp > 0 else 0

        # Education (10)
        resume_edu = self.extract_education(resume_text)
        jd_edu = self.extract_education(job_description)
        edu_score = 10 if resume_edu and (resume_edu in jd_edu or jd_edu in resume_edu) else 5 if resume_edu else 0

        # Contact Info/Formatting (10)
        contact = self.extract_contact_info(resume_text)
        contact_score = sum(contact.values()) / 3 * 10

        # Semantic Similarity (15)
        semantic_sim = self.semantic_similarity(resume_text, job_description)
        semantic_score = int(semantic_sim * 15)

        final_score = round(skills_score + keyword_score + exp_score + edu_score + contact_score + semantic_score)
        breakdown = {
            'skills_score': round(skills_score, 1),
            'keyword_score': round(keyword_score, 1),
            'exp_score': exp_score,
            'edu_score': edu_score,
            'contact_score': round(contact_score, 1),
            'semantic_score': semantic_score,
            'semantic_similarity': round(semantic_sim, 3),
            'matched_skills': list(matched_skills),
            'missing_skills': list(jd_skills - resume_skills),
            'matched_keywords': list(matched_keywords),
            'missing_keywords': list(jd_keywords - resume_keywords),
            'resume_exp': resume_exp,
            'jd_exp': jd_exp,
            'resume_edu': resume_edu,
            'jd_edu': jd_edu,
            'contact': contact
        }
        recommendations = []
        if breakdown['missing_skills']:
            recommendations.append(f"Add missing skills: {', '.join(breakdown['missing_skills'][:5])}")
        if breakdown['missing_keywords']:
            recommendations.append(f"Add missing keywords: {', '.join(breakdown['missing_keywords'][:5])}")
        if exp_score < 15:
            recommendations.append("Highlight more relevant experience.")
        if edu_score < 10:
            recommendations.append("Add or clarify your education details.")
        if contact_score < 10:
            recommendations.append("Add missing contact info (email, phone, LinkedIn).")
        if semantic_score < 10:
            recommendations.append("Improve contextual match with the job description.")
        return {
            'final_score': final_score,
            'score_description': f'ATS Score: {final_score}/100',
            'breakdown': breakdown,
            'recommendations': recommendations,
            'skills_matched': len(matched_skills),
            'skills_missing': len(jd_skills - resume_skills)
        } 