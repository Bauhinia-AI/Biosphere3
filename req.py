import requests

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
        {"method": "post", "route": "trade", "data": {"merchantid": 1, "merchantnum": 1, "transactiontype": 0}},
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

if __name__ == "__main__":
    run_tests()