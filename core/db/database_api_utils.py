import httpx

BASE_URL = "http://47.95.21.135:8085"
# BASE_URL = "http://localhost:8085"


# 异步函数
async def make_api_request_async(
    method: str, endpoint: str, params: dict = None, data: dict = None
):
    url = f"{BASE_URL}{endpoint}"
    method = method.upper()

    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url, params=params)
            else:
                response = await client.request(method, url, json=data)

            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise Exception(f"API request to {url} failed: {e}")
        except httpx.HTTPStatusError as e:
            raise Exception(
                f"API request to {url} failed with status code {e.response.status_code}"
            )


# 同步函数
def make_api_request_sync(
    method: str, endpoint: str, params: dict = None, data: dict = None
):
    url = f"{BASE_URL}{endpoint}"
    method = method.upper()

    try:
        with httpx.Client() as client:
            if method == "GET":
                response = client.get(url, params=params)
            else:
                response = client.request(method, url, json=data)

        response.raise_for_status()  # 如果状态码不是 2xx，会抛出异常

        return response.json()  # 返回 JSON 响应
    except httpx.RequestError as e:
        raise Exception(f"API request to {url} failed: {e}")
    except httpx.HTTPStatusError as e:
        raise Exception(
            f"API request to {url} failed with status code {e.response.status_code}"
        )


if __name__ == "__main__":
    import asyncio

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

    # # 使用同步函数
    # endpoint = "/update_meta_seq"
    # print(make_api_request_sync("POST", endpoint, data=data))

    # # 使用异步函数
    # async def test_async():
    #     print(await make_api_request_async("POST", endpoint, data=data))

    # asyncio.run(test_async())

    # 测试存储和检索印象

    # 存储印象
    impression_data = {"from_id": 1, "to_id": 2, "impression": "Seems friendly."}
    endpoint = "/store_impression"
    response = make_api_request_sync("POST", endpoint, data=impression_data)
    print("Storing Impression:", response)

    # 检索印象
    get_impression_data = {
        "from_id": 1,
        "to_id": 2,
        "k": 1,
    }

    endpoint = "/get_impression"
    response = make_api_request_sync("POST", endpoint, data=get_impression_data)
    print("Retrieving Impression:", response)
