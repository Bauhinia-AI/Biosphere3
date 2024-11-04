import os
import json
from langchain_openai import ChatOpenAI

os.environ["OPENAI_API_KEY"] = "sk-tejMSVz1e3ziu6nB0yP2wLiaCUp2jR4Jtf4uaAoXNro6YXmh"


class ActionListGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(base_url="https://api.aiproxy.io/v1", model="gpt-4o")
        self.locations = """
        school,workshop,home,farm,mall,square,hospital,fruit,harvest,fishing,mine,orchard
        """
        self.commands = """
        1. goto [location]
        2. pickapple [number]
        3. gofishing [number]
        4. harvest [number]
        5. sleep [hours]
        6. study [hours]
        7. seedoctor [number]
        8. gomining [number]
        9. work [hours]
        10. use [inventory]
        11. getmycv
        12. submitcv [doctor/teacher] [content of cv]
        13. getvoteinfo
        14. votefor [playername]
        15. stop
        16. buy [inventory] [number]
        17. sell [inventory] [number]
        18. sendmsg [playername/id] [content of msg]
        19. showallitem
        20. getprice [inventory]
        """
        self.inventory = """
        ore,bread,apple,wheat,fish
        """
        self.constraints = """
        1. pick_apple(): Must have enough energy and be in the orchard.
        2. go_fishing(): Must have enough energy and be in the fishing area.
        3. mine(): Must have enough energy and be in the mine.
        4. harvest(): Must have enough energy and be in the harvest area.
        5. buy(itemType, amount): Must have enough money and items must be available.
        6. sell(itemType, amount): Must have enough items in inventory.
        7. use_item(itemType, amount): Must have enough items in inventory.
        8. see_doctor(hours): Must have enough money and be in the hospital.
        9. sleep(hours): Must be at home.
        10. study(hours): Must be in school and have enough money.
        11. nav(placeName): Must be in one of the specified locations.
        """
        self.prompt_template = """
        Character Profile: {character_profile}
        Memory: {memory}
        Status: {status}
        The character can navigate to the following locations: {locations}
        Supported commands: {commands}
        Supported inventory: {inventory}
        Constraints: {constraints}
        Based on the character's personality, memory, and status information, generate a list of commands for the character to perform.
        Only output the list of commands in JSON array format and nothing else, make sure the commands are in a logical order to avoid errors.
        Here is an example format that you should follow strictly:
        {example}
        """
        self.example = json.dumps(
            [
                "goto orchard",
                "pickapple 10",
                "sell apple 7",
                "goto home",
                "sleep 8",
            ]
        )

    def generate_prompt(self, character_profile, memory, status):
        return self.prompt_template.format(
            character_profile=character_profile,
            memory=memory,
            status=status,
            locations=self.locations,
            commands=self.commands,
            inventory=self.inventory,
            constraints=self.constraints,
            example=self.example,
        )

    def generate_action_list(self, character_profile, memory, status):
        prompt = self.generate_prompt(character_profile, memory, status)
        response = self.llm.invoke(prompt)
        action_list = response.content.strip()

        # Debug: Print the raw response
        print("Raw LLM Response:", action_list)

        # Remove Markdown code block if present
        if action_list.startswith("```json"):
            action_list = action_list[7:-3].strip()

        # Ensure the response is a valid JSON array
        if not (action_list.startswith("[") and action_list.endswith("]")):
            raise ValueError("LLM returned an invalid JSON array.")

        # Attempt to parse the JSON
        try:
            return json.loads(action_list)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}")


# Example usage
if __name__ == "__main__":
    action_list_generator = ActionListGenerator()
    character_profile = (
        "The character is energetic, and the goal is to earn as much money as possible."
    )
    memory = "The character has recently caught 10 fish and picked 10 apples."
    status = "Energy: 100, Health:100, Money: 20, Hungry: 100, Study XP: 0, Education Level: PrimarySchool"
    try:
        action_list = action_list_generator.generate_action_list(
            character_profile, memory, status
        )
        print("Generated Action List:")
        print(action_list)
    except ValueError as e:
        print("Error:", e)
