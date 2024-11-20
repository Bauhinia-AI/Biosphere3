import httpx

BASE_URL = "http://47.95.21.135:8082"


# 异步函数
async def make_api_request_async(
    method: str,
    endpoint: str,
    params: dict = None,
    data: dict = None,
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
    method: str,
    endpoint: str,
    params: dict = None,
    data: dict = None,
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
