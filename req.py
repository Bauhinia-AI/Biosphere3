import requests

file_list = ['/trade', "/character/data", "/character/status", "/character/bsinfo",'/character/inventory']
base_url = "http://localhost:8000"

for file_name in file_list:
    url = base_url + file_name
    response = requests.get(url)

    print("Status Code:", response.status_code)
    print("Response Body:", response.json())