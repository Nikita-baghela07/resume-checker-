import sys, os
sys.path.insert(0, os.path.dirname(os.getcwd()))
from app.services import scoring_service
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

resume = "I am a professional baker. I love baking cakes and making pastries with flour, sugar, and yeast."

jd = '''We are looking for a Software Engineer with 2+ years of experience in Python and REST APIs.
You will build scalable web services and work with cloud technologies like AWS and Docker.'''

scores = scoring_service.compute_scores(resume, jd, model)
print('Total (Spam vs JD):', scores.overall)
