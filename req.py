import requests


class Request:
    def __init__(self, url):
        self.url = url

    def post(self, route, data):
        response = requests.post(self.url + route, json=data)
        return response

    def get(self):
        response = requests.get(self.url)
        return response


if __name__ == "__main__":
    url = "http://localhost:8000/"
    # route = "work-change"
    # data = {"jobid": 5}

    # route = "trade"
    # data = {"merchantid": 1, "merchantnum": 1, "transactiontype": 0}

    # route = "use"
    # data = {"merchantid": 2, "merchantnum": 1}

    # route = "see-doctor"
    # data = {}
    route = "sleep"
    data = {"timelength": 10}

    req = Request(url)
    response = req.post(route, data)

    print("Status Code:", response.status_code)
    print("Response Body:", response.json())
