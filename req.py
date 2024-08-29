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


if __name__ == "__main__":
    test_work_change()
    test_study()
    test_talk()
    test_end_talk()
    test_go_to()
    test_distance()
