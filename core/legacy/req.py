import requests


file_list = [
    "/trade",
    "/character/data",
    "/character/status",
    "/character/bsinfo",
    "/character/inventory",
]
base_url = "http://localhost:8000"


# Base URL
base_url = "http://localhost:8000"


# Test /work-change
def test_work_change():
    url = f"{base_url}/work-change"
    data = {"jobid": 5}
    response = requests.post(url, json=data)
    print("Work Change - Status Code:", response.status_code)
    print("Work Change - Response Body:", response.json())


def test_study():
    url = f"{base_url}/study"
    data = {"timelength": 3}
    response = requests.post(url, json=data)
    print("Study - Status Code:", response.status_code)
    print("Study - Response Body:", response.json())


def test_talk():
    url = f"{base_url}/talk"
    data = {"userid": "user456", "talkcontent": "Hello!"}
    response = requests.post(url, json=data)
    print("Talk - Status Code:", response.status_code)
    print("Talk - Response Body:", response.json())


def test_end_talk():
    url = f"{base_url}/end-talk"
    data = {"userid": "user456", "talkid": "1234abcd"}
    response = requests.post(url, json=data)
    print("End Talk - Status Code:", response.status_code)
    print("End Talk - Response Body:", response.json())


def test_go_to():
    url = f"{base_url}/go-to"
    data = {"to": "100,200"}
    response = requests.post(url, json=data)
    print("Go To - Status Code:", response.status_code)
    print("Go To - Response Body:", response.json())


def test_distance():
    url = f"{base_url}/distance"
    data = {"from_": "0,0", "to": "3,4"}
    response = requests.post(url, json=data)
    print("Distance - Status Code:", response.status_code)
    print("Distance - Response Body:", response.json())


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


def test_get_candidates():
    url = f"{base_url}/candidates"
    response = requests.get(url)
    print("Get Candidates - Status Code:", response.status_code)
    print("Get Candidates - Response Body:", response.json())


class Request:
    def __init__(self, url):
        self.url = url

    def post(self, route, data):
        response = requests.post(self.url + route, json=data)
        return response

    def get(self, route, data):
        response = requests.get(self.url + route, params=data)
        return response


def run_tests():
    url = "http://localhost:8000/"
    req = Request(url)

    test_cases = [
        {"method": "post", "route": "work-change", "data": {"jobid": 5}},
        {
            "method": "post",
            "route": "trade",
            "data": {"merchantid": 1, "merchantnum": 1, "transactiontype": 0},
        },
        {"method": "post", "route": "use", "data": {"merchantid": 2, "merchantnum": 1}},
        {"method": "post", "route": "see-doctor", "data": {}},
        {"method": "post", "route": "sleep", "data": {"timelength": 10}},
        {"method": "get", "route": "activity", "data": {"subjectid": 4}},
        {"method": "get", "route": "position", "data": None},
    ]

    for test in test_cases:
        method = test["method"]
        route = test["route"]
        data = test["data"]

        if method == "post":
            response = req.post(route, data)
        elif method == "get":
            response = req.get(route, data)

        print(f"Testing {method.upper()} {route}")
        print("Status Code:", response.status_code)
        print("Response Body:", response.json())
        print("-" * 40)

    test_work_change()
    test_resume_submission()
    test_vote()
    test_public_job()
    test_freelance_job()
    test_get_candidates()


if __name__ == "__main__":
    run_tests()
