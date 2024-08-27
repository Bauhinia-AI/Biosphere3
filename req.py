import requests

# Base URL
base_url = "http://localhost:8000"

# Test /work-change
def test_work_change():
    url = f"{base_url}/work-change"
    data = {"jobid": 5}
    response = requests.post(url, json=data)
    print("Work Change - Status Code:", response.status_code)
    print("Work Change - Response Body:", response.json())

# Test /resume-submission
def test_resume_submission():
    url = f"{base_url}/resume-submission"
    data = {"jobid": 2, "cvurl": "http://example.com/cv.pdf"}
    response = requests.post(url, json=data)
    print("Resume Submission - Status Code:", response.status_code)
    print("Resume Submission - Response Body:", response.json())

# Test /vote
def test_vote():
    url = f"{base_url}/vote"
    data = {"userid": "user123"}
    response = requests.post(url, json=data)
    print("Vote - Status Code:", response.status_code)
    print("Vote - Response Body:", response.json())

# Test /public-job
def test_public_job():
    url = f"{base_url}/public-job"
    data = {"jobid": 4, "timelength": 5}
    response = requests.post(url, json=data)
    print("Public Job - Status Code:", response.status_code)
    print("Public Job - Response Body:", response.json())

# Test /freelance-job
def test_freelance_job():
    url = f"{base_url}/freelance-job"
    data = {"timelength": 3, "merchantid": 1}
    response = requests.post(url, json=data)
    print("Freelance Job - Status Code:", response.status_code)
    print("Freelance Job - Response Body:", response.json())

if __name__ == "__main__":
    test_work_change()
    test_resume_submission()
    test_vote()
    test_public_job()
    test_freelance_job()