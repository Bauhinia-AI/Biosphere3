# database_api_utils.py
import httpx
import asyncio
import os
import logging
import time

# 在项目根目录下创建 logs 文件夹
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
    handlers=[
        logging.FileHandler(os.path.join(log_directory, "database_api_utils.log")),
        logging.StreamHandler(),
    ],
)

BASE_URL = "http://47.95.21.135:8085"
# BASE_URL = "http://localhost:8085"


async def make_api_request_async(
    method: str, endpoint: str, data: dict = None, retries: int = 3, delay: int = 2
):
    url = f"{BASE_URL}{endpoint}"
    method = method.upper()

    for attempt in range(retries):
        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:  # Set timeout to 30 seconds
            try:
                if method == "GET":
                    response = await client.get(url, params=data)
                else:
                    response = await client.request(method, url, json=data)

                response.raise_for_status()
                response_data = response.json()

                # Check if `code` is not 1
                if response_data["code"] != 1:
                    logging.warning(
                        "Error detected in response from endpoint %s: %s",
                        endpoint,
                        response_data["message"],
                    )
                else:
                    logging.info(response_data["message"])

                return response_data

            except httpx.TimeoutException as e:
                logging.warning(
                    f"Attempt {attempt + 1}/{retries} failed: Request timed out"
                )
                logging.error(f"Error details: {str(e)}")
                if attempt < retries - 1:
                    logging.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    raise Exception(
                        f"API request to {url} failed after {retries} attempts due to timeout. Error details: {str(e)}"
                    )

            except httpx.RequestError as e:
                logging.warning(
                    f"Attempt {attempt + 1}/{retries} failed: Request error"
                )
                logging.error(f"Error details: {str(e)}")
                if attempt < retries - 1:
                    logging.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    raise Exception(
                        f"API request to {url} failed after {retries} attempts. Error details: {str(e)}"
                    )

            except httpx.HTTPStatusError as e:
                logging.warning(
                    f"Attempt {attempt + 1}/{retries} failed: HTTP status error"
                )
                logging.error(f"Status code: {e.response.status_code}")
                logging.error(f"Response content: {e.response.text}")
                if attempt < retries - 1:
                    logging.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    raise Exception(
                        f"API request to {url} failed after {retries} attempts, status code: {e.response.status_code}. Response content: {e.response.text}"
                    )


# Synchronous function
def make_api_request_sync(
    method: str, endpoint: str, data: dict = None, retries: int = 3, delay: int = 2
):
    url = f"{BASE_URL}{endpoint}"
    method = method.upper()

    for attempt in range(retries):
        try:
            with httpx.Client(timeout=30) as client:  # Set timeout
                if method == "GET":
                    response = client.get(url, params=data)
                else:
                    response = client.request(method, url, json=data)

            response.raise_for_status()
            response_data = response.json()

            # Check if `code` is not 1
            if response_data["code"] != 1:
                logging.warning(
                    "Error detected in response from endpoint %s: %s",
                    endpoint,
                    response_data["message"],
                )
            else:
                logging.info(response_data["message"])

            return response_data

        except httpx.RequestError as e:
            logging.warning(f"Attempt {attempt + 1}/{retries} failed: {e}")
            logging.error(f"Error type: {type(e).__name__}")
            logging.error(f"Error details: {str(e)}")
            if attempt < retries - 1:
                logging.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise Exception(
                    f"API request to {url} failed after {retries} attempts. Error type: {type(e).__name__}, Error details: {str(e)}"
                )

        except httpx.HTTPStatusError as e:
            logging.warning(f"Attempt {attempt + 1}/{retries} failed: {e}")
            logging.error(f"Status code: {e.response.status_code}")
            logging.error(f"Response content: {e.response.text}")
            if attempt < retries - 1:
                logging.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise Exception(
                    f"API request to {url} failed after {retries} attempts, status code: {e.response.status_code}. Response content: {e.response.text}"
                )
