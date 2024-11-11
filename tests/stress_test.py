# tests/stress_test.py

import asyncio
import aiohttp
import time
import random
import matplotlib.pyplot as plt
import sys
import os

# Ensure the parent directory is in sys.path so we can import modules from the main project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.create_database import DatabaseSetupApp  # Import DatabaseSetupApp

API_BASE_URL = "http://localhost:8085"


async def send_store_action(session, characterId, action_id):
    """
    Send a single /store_action request and return the response time.
    """
    url = f"{API_BASE_URL}/store_action"
    data = {
        "characterId": characterId,
        "meta_action": "Test Action",
        "description": "This is a test action",
        "response": True,
        "action_id": action_id,
        "prev_action": action_id - 1 if action_id > 1 else None,
    }
    start_time = time.perf_counter()
    try:
        async with session.post(url, json=data) as response:
            await response.json()
    except Exception as e:
        print(f"Request failed: {e}")
        return None
    end_time = time.perf_counter()
    return end_time - start_time


async def run_stress_test(concurrent_users):
    """
    Run the stress test, simulating the specified number of concurrent users, each sending one request.
    """
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(concurrent_users):
            characterId = random.randint(1, 1000000)
            action_id = random.randint(1, 1000000000)
            task = asyncio.create_task(
                send_store_action(session, characterId, action_id)
            )
            tasks.append(task)
        response_times = await asyncio.gather(*tasks)
    return response_times


def reset_database():
    """
    Reset the action collection in the database by dropping and recreating it.
    """
    # Initialize the DatabaseSetupApp and reset the action database
    app = DatabaseSetupApp()
    app.setup_action_database()


def main():
    # Define the list of concurrent user counts to test, from 100 to 10,000, step 100
    concurrent_user_list = list(range(100, 10001, 100))
    avg_response_times = []
    success_rates = []

    for concurrent_users in concurrent_user_list:
        print(f"Stress testing with {concurrent_users} concurrent users")

        # Reset the database before each test
        reset_database()

        loop = asyncio.get_event_loop()
        response_times = loop.run_until_complete(run_stress_test(concurrent_users))

        # Filter out failed requests (None)
        successful_response_times = [rt for rt in response_times if rt is not None]
        total_requests = len(response_times)
        successful_requests = len(successful_response_times)
        success_rate = (
            (successful_requests / total_requests) * 100 if total_requests > 0 else 0
        )
        success_rates.append(success_rate)

        if successful_requests > 0:
            avg_response_time = sum(successful_response_times) / successful_requests
            avg_response_times.append(avg_response_time)
            print(
                f"Average response time: {avg_response_time:.4f} seconds | Success rate: {success_rate:.2f}%"
            )
        else:
            avg_response_times.append(float("inf"))  # Indicates all requests failed
            print(f"All {concurrent_users} requests failed.")

    # Plot the response time graph
    plt.figure(figsize=(14, 7))
    plt.plot(
        concurrent_user_list,
        avg_response_times,
        marker="o",
        label="Average Response Time",
    )
    plt.xlabel("Number of Concurrent Users")
    plt.ylabel("Average Response Time (seconds)")
    plt.title("Stress Test: Average Response Time vs. Concurrent Users")
    plt.grid(True)
    plt.legend()
    plt.savefig("stress_test_response_time.png")
    plt.show()

    # Plot the success rate graph
    plt.figure(figsize=(14, 7))
    plt.plot(
        concurrent_user_list,
        success_rates,
        marker="x",
        color="red",
        label="Success Rate (%)",
    )
    plt.xlabel("Number of Concurrent Users")
    plt.ylabel("Success Rate (%)")
    plt.title("Stress Test: Success Rate vs. Concurrent Users")
    plt.grid(True)
    plt.legend()
    plt.savefig("stress_test_success_rate.png")
    plt.show()


if __name__ == "__main__":
    main()
