from req import Request

BASE_URL = "http://localhost:8000/"


def run_tests():
    req = Request(BASE_URL)

    test_cases = [
        {"method": "post", "route": "work-change", "data": {"jobid": 2}},
        {
            "method": "post",
            "route": "trade",
            "data": {"merchantid": 1, "merchantnum": 1, "transactiontype": 0},
        },
        {"method": "post", "route": "use", "data": {"merchantid": 2, "merchantnum": 1}},
        {"method": "post", "route": "see-doctor", "data": {}},
        {"method": "post", "route": "sleep", "data": {"timelength": 10}},
        {"method": "get", "route": "character/data", "data": None},
        {"method": "get", "route": "character/status", "data": None},
        {"method": "get", "route": "character/bsinfo", "data": None},
        {"method": "get", "route": "character/inventory", "data": None},
        {
            "method": "post",
            "route": "resume-submission",
            "data": {"jobid": 1, "cvurl": "http://example.com/cv"},
        },
        {"method": "post", "route": "vote", "data": {"userid": "user123"}},
        {
            "method": "post",
            "route": "public-job",
            "data": {"jobid": 1, "timelength": 5},
        },
        {"method": "post", "route": "study", "data": {"timelength": 3}},
        {
            "method": "post",
            "route": "talk",
            "data": {"userid": "user456", "talkcontent": "Hello!"},
        },
        {
            "method": "post",
            "route": "end-talk",
            "data": {"userid": "user456", "talkid": "1234abcd"},
        },
        {"method": "post", "route": "go-to", "data": {"to": "Farm"}},
        {"method": "post", "route": "distance", "data": {"to": "3,4"}},
        {"method": "post", "route": "freelance-job", "data": {"timelength": 4}},
        {"method": "get", "route": "freelance-jobs", "data": None},
        {"method": "get", "route": "public-jobs", "data": None},
        {"method": "get", "route": "candidates", "data": None},
        {"method": "get", "route": "activity", "data": {"subjectid": 1}},
        {"method": "get", "route": "talk_data", "data": {"talkid": "1234abcd"}},
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
        break
        print("-" * 40)


if __name__ == "__main__":
    run_tests()
