from langchain_core.tools import tool
import requests

@tool
def do_freelance_job(timelength: int, merchantid: int = None):
    """
    Do a freelance job for a given number of hours.
    """
    url = "http://localhost:8000/freelance-job"
    data = {"timelength": timelength, "merchantid": merchantid}
    response = requests.post(url, json=data)
    return response.json()

@tool
def navigate_to(to: str):
    """
    Navigate to a given location.
    """
    url = "http://localhost:8000/go-to"
    data = {"to": to}
    response = requests.post(url, json=data)
    return response.json()

@tool
def sleep(timelength: int):
    """
    Sleep for a given number of hours.
    """
    url = "http://localhost:8000/sleep"
    data = {"timelength": timelength}
    response = requests.post(url, json=data)
    return response.json()

print(sleep.invoke({"timelength": 10}))
print(navigate_to.invoke({"to": "Farm"}))
print(do_freelance_job.invoke({"timelength": 10}))