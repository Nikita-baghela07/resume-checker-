import sys, os, requests

# Get token
login_res = requests.post("http://localhost:8000/login", data={"username": "test@test.com", "password": "password"})
token = login_res.json().get("access_token")

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

with open('data/sample_resumes/weak_resume.txt', 'r', encoding='utf-8') as f:
    resume = f.read()

jd = '''We are looking for a Software Engineer with 2+ years of experience in Python and REST APIs.
You will build scalable web services and work with cloud technologies like AWS and Docker.'''

print('Sending optimize request...')
res = requests.post("http://localhost:8000/api/v1/optimize", json={"resume_text": resume, "job_description": jd}, headers=headers)
print('Status:', res.status_code)
if res.status_code == 200:
    data = res.json()
    print('Initial Score:', data['scores']['initial']['overall'])
    print('Final Score:', data['scores']['optimized']['overall'])
else:
    print('Error:', res.text)
