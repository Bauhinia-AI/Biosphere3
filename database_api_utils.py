import requests
from req import Request

BASE_URL = "http://47.95.21.135:8085"


# 异步函数
async def make_api_request_async(
    method: str, endpoint: str, params: dict = None, data: dict = None
):
    url = f"{BASE_URL}{endpoint}"
    method = method.upper()
    if method == "GET":
        request = Request(method, url, params=params)
    else:
        request = Request(method, url, json=data)

    response = await request.send()

    if response.status_code == 200:
        return await response.json()
    else:
        raise Exception(
            f"API request to {url} failed with status code {response.status_code}"
        )


# 同步函数
def make_api_request_sync(
    method: str, endpoint: str, params: dict = None, data: dict = None
):
    url = f"{BASE_URL}{endpoint}"
    method = method.upper()

    try:
        if method == "GET":
            response = requests.get(url, params=params)
        else:
            response = requests.post(url, json=data)

        response.raise_for_status()  # 如果状态码不是 2xx，会抛出异常

        return response.json()  # 返回 JSON 响应
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request to {url} failed: {e}")


if __name__ == "__main__":
    sample_state = {
        "userid": 102,
        "input": "Sample input for the daily objective.",
        "plan": ["Step 1", "Step 2"],
        "past_steps": [("step1", "result1")],
        "response": "Sample response",
        "daily_objective": ["Objective 1", "Objective 2"],
        "meta_seq": ["Action 1", "Action 2"],
        "tool_functions": "function1",
        "locations": "location1",
        "past_objectives": [["Objective A"], ["Objective B"]],
        "execution_results": [{"result": "success"}],
        "reflection": "Reflection text",
        "messages": ["Message 1", "Message 2"],
    }
    data = {
        "userid": sample_state["userid"],
        "meta_sequence": sample_state["meta_seq"],
    }
    # Make API request to update_meta_seq
    endpoint = "/update_meta_seq"
    print(make_api_request_sync("POST", endpoint, data=data))
