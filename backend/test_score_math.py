import sys, os
sys.path.insert(0, os.path.dirname(os.getcwd()))
from app.services import scoring_service
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

with open('../data/sample_resumes/weak_resume.txt', 'r', encoding='utf-8') as f:
    resume = f.read()

jd = '''We are looking for a Software Engineer with 2+ years of experience in Python and REST APIs.
You will build scalable web services and work with cloud technologies like AWS and Docker.'''

scores = scoring_service.compute_scores(resume, jd, model)
print('Total:', scores.overall)
print('Skills:', scores.skills_match)
print('Experience:', scores.experience_match)
print('Keyword:', scores.keyword_coverage)
