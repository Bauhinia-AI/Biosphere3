import os
from langchain_openai import ChatOpenAI
from datetime import datetime, timedelta
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from task_scheduler import Task
import json

os.environ["OPENAI_API_KEY"] = "sk-tejMSVz1e3ziu6nB0yP2wLiaCUp2jR4Jtf4uaAoXNro6YXmh"


class TaskGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini")
        self.prompt_template = """
            Task Description: {task_description}
            Based on the above task description, extract the necessary information to construct a Task object. The information should include:
            - Start time (in ISO 8601 format, e.g., "2023-10-01T10:00:00" for specific dates, or "now + 10 minutes" for relative times)
            - Duration (in seconds, if not provided, set to 60 seconds)
            - Priority (an integer value, if not provided, set to 1)

            Here is a specific example, you should follow the JSON format strictly, you should only output the JSON:
            When the task description is "pick 10 apples in 10 mins after ten minutes, but you should in the orchard first", the extracted information is as follows:
            {{
                "id": 1,
                "constraints": "In the orchard",
                "start_time": "datetime.now() + timedelta(minutes=10)",
                "duration": 60,
                "priority": 1
            }}
        """

    def generate_prompt(self, task_description):
        return self.prompt_template.format(task_description=task_description)

    def generate_task(self, task_description):
        prompt = self.generate_prompt(task_description)
        response = self.llm.invoke(prompt)
        task_info = response.content

        # Parse the task_info to extract task details
        task_data = self.parse_task_info(task_info)

        # Create and return a Task object
        task = Task(
            id=task_data["id"],
            task_description=task_description,
            constraints=task_data["constraints"],
            start_time=task_data["start_time"],
            duration=task_data["duration"],
            priority=task_data["priority"],
        )
        return task

    def parse_task_info(self, task_info):
        task_data = json.loads(task_info)
        task_data["start_time"] = datetime.fromisoformat(task_data["start_time"])
        return task_data


# Example usage
if __name__ == "__main__":
    task_generator = TaskGenerator()
    task_description = "catch 3 fish in 10 mins after ten minutes, but you should in the fishing first"
    task = task_generator.generate_task(task_description)
    print(
        f"Generated Task: ID={task.id}, Description={task.task_description}, Start Time={task.start_time}, Duration={task.duration}, Priority={task.priority}"
    )
