import os
from langchain_openai import ChatOpenAI

os.environ["OPENAI_API_KEY"] = "sk-tejMSVz1e3ziu6nB0yP2wLiaCUp2jR4Jtf4uaAoXNro6YXmh"


class CommandGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini")
        self.supported_commands = """
        1. goto [school/workshop/home/farm/mall/square/hospital/fruit/harvest/fishing/mine/orchard]
        2. pickapple [number]
        3. gofishing [number]
        4. harvest [number]
        5. sleep [hours]
        6. study [hours]
        7. seedoctor [number]
        8. gomining [number]
        9. work [hours]
        10. use [ore/bread/apple/wheat/fish]
        11. getmycv
        12. submitcv [doctor/teacher] [content of cv]
        13. getvoteinfo
        14. votefor [playername]
        15. stop
        16. buy [ore/bread/apple/wheat/fish] [number]
        17. sell [ore/bread/apple/wheat/fish] [number]
        18. sendmsg [playername/id] [content of msg]
        19. showallitem
        20. getprice [ore/bread/apple/wheat/fish]
        """
        self.example = {
            "description": "buy ten fish",
            "request": {
                "characterId": 1,
                "messageCode": 2,
                "messageName": "singleAction",
                "data": {"command": "buy fish 10"},
            },
        }
        self.prompt_template = """
        Task Description: {task_description}
        Based on the above task description, extract the necessary command and parameters from the task description, choose an appropriate command from the supported commands below, and only return the command.
        Here are the currently supported commands:
        {supported_commands}

        Here is a specific example:
        When the task description is {example_description}, the command is as follows:
        {example_command}
        """

    def generate_prompt(self, task_description):
        return self.prompt_template.format(
            task_description=task_description,
            supported_commands=self.supported_commands,
            example_description=self.example["description"],
            example_command=self.example["request"]["data"]["command"],
        )

    def generate_single_command_body(self, task_description, character_id):
        prompt = self.generate_prompt(task_description)
        response = self.llm.invoke(prompt)
        command_data = response.content

        request_body = {
            "characterId": character_id,
            "messageCode": 2,
            "messageName": "singleAction",
            "data": {"command": command_data},
        }
        return request_body


# Example usage
if __name__ == "__main__":
    command_generator = CommandGenerator()
    task_description = "去抓7条鱼"
    character_id = 42
    command = command_generator.generate_single_command_body(
        task_description, character_id
    )
    print(command)
