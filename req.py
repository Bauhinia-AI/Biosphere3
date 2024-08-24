import requests

url = "http://localhost:8000/work-change"
data = {"jobid": 5}

response = requests.post(url, json=data)

print("Status Code:", response.status_code)
print("Response Body:", response.json())