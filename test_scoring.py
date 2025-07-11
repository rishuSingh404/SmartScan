import unittest
from scoring import ResumeScorer

class TestResumeScorer(unittest.TestCase):
    def setUp(self):
        self.scorer = ResumeScorer()
        self.sample_resume = """
        John Doe
        Email: john.doe@email.com
        Phone: 1234567890
        LinkedIn: linkedin.com/in/johndoe
        Experience: 3 years in Python development, data-analysis, and machine-learning.
        My skills include python, data-analysis, machine-learning, teamwork, and communication.
        Education: Bachelor of Technology in Computer Science
        """
        self.sample_jd = """
        We are looking for a candidate with experience in Python, data-analysis, and machine-learning.
        Required skills are python, data-analysis, machine-learning, and communication.
        Education: B.Tech or equivalent
        Experience: 2+ years
        """

    def test_keyword_extraction(self):
        resume_keywords = self.scorer.extract_keywords(self.sample_resume)
        jd_keywords = self.scorer.extract_keywords(self.sample_jd)
        matched_keywords = resume_keywords & jd_keywords
        self.assertIn('python', matched_keywords)
        self.assertIn('analysis', matched_keywords)
        self.assertIn('machine', matched_keywords)
        self.assertIn('learning', matched_keywords)
        self.assertIn('communication', matched_keywords)

    def test_ats_scoring(self):
        result = self.scorer.score_resume(self.sample_resume, self.sample_jd)
        print("Resume extracted skills:", self.scorer.extract_skills(self.sample_resume))
        print("JD extracted skills:", self.scorer.extract_skills(self.sample_jd))
        print("Matched skills:", result['breakdown']['matched_skills'])
        self.assertGreater(result['final_score'], 0)
        self.assertGreater(result['skills_matched'], 0)
        self.assertIn('python', result['breakdown']['matched_skills'])
        self.assertIn('data-analysis', result['breakdown']['matched_skills'])
        self.assertIn('machine-learning', result['breakdown']['matched_skills'])

if __name__ == '__main__':
    unittest.main() 