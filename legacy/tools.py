# from langchain_core.tools import tool
# import requests
import time
import random

from langchain_core.tools import tool

@tool
def submit_cv(targetOccupation: str, content: str) -> dict:
    #simulate time consumed
    time_consumed = random.uniform(0.1, 1.0)
    time.sleep(time_consumed)
    """Submit a resume for a public job.
    
    Args:
        targetOccupation (str): The occupation for which the resume is being submitted. Must be one of (Teacher, Doctor).
        content (str): The content of the resume.
    
    Constraints:
        - Can only be submitted on ResumeSubmitDay, which is Saturday.
    
    Returns:
        dict: A simulated response indicating the success of the resume submission.
    """
    return {
        "characterId": 1,
        "messageCode": 3,
        "messageName": "actionresult",
        "data": {
            "actionName": "submit_cv",
            "actionCode": 1,
            "result": True,
            "gameTime": "12:23:10",
            "msg": f"Resume submitted successfully for {targetOccupation}."
        }
    }

@tool
def vote(candidateName: str) -> dict:
    time_consumed = random.uniform(0.1, 1.0)
    time.sleep(time_consumed)
    """Cast a vote for a candidate.
    
    Args:
        candidateName (str): The name of the candidate to vote for.
    
    Constraints:
        - Can only vote on VoteDay, which is Sunday.
    
    Returns:
        dict: A simulated response indicating the success of the voting action.
    """
    return {
        "characterId": 1,
        "messageCode": 3,
        "messageName": "actionresult",
        "data": {
            "actionName": "vote",
            "actionCode": 1,
            "result": True,
            "gameTime": "12:23:10",
            "msg": f"Voted successfully for {candidateName}."
        }
    }
import random
@tool
def work_as_public_occupation(hours: int) -> dict:
    time_consumed = random.uniform(0.1, 1.0)
    time.sleep(time_consumed)
    """Perform work as a public occupation (e.g., teacher or doctor).
    
    Args:
        hours (int): The number of hours to work.
    
    Constraints:
        - Must have a public occupation.
        - Must be in the workplace.
        - Must have enough energy.
    
    Returns:
        dict: A simulated response indicating the success of the work action.
    """
    return {
        "characterId": 1,
        "messageCode": 3,
        "messageName": "actionresult",
        "data": {
            "actionName": "work_as_public_occupation",
            "actionCode": 1,
            "result": True,
            "gameTime": "12:23:10",
            "msg": f"Worked as public occupation for {hours} hours."
        }
    }

@tool
def pick_apple() -> dict:
    time_consumed = random.uniform(0.1, 1.0)
    time.sleep(time_consumed)
    """Pick an apple, costing energy.
    
    Constraints:
        - Must have enough energy.
        - Must be in the orchard.
    
    Returns:
        dict: A simulated response indicating the success of the apple picking action.
    """
    result = random.choice(["successfully", "unsuccessfully"])
    reason_map = {
        "successfully": "picked an apple successfully",
        "unsuccessfully": "failed to pick an apple because you don't have enough energy or you are not in the orchard"
    }
    return {
        "characterId": 1,
        "messageCode": 3,
        "messageName": "actionresult",
        "data": {
            "actionName": "pickapple",
            "actionCode": 1,
            "result": result == "successfully",
            "gameTime": "12:23:10",
            "msg": f"Picked an apple {reason_map[result]}."
        }
    }

@tool
def go_fishing() -> dict:
    time_consumed = random.uniform(0.1, 1.0)
    time.sleep(time_consumed)
    """Fish for resources, costing energy.
    
    Constraints:
        - Must have enough energy.
        - Must be in the fishing area.
    
    Returns:
        dict: A simulated response indicating the success of the fishing action.
    """
    result = random.choice(["successfully", "unsuccessfully"])
    reason_map = {
        "successfully": "went fishing successfully",
        "unsuccessfully": "failed to go fishing because you don't have enough energy or you are not in the fishing area"
    }
    return {
        "characterId": 1,
        "messageCode": 3,
        "messageName": "actionresult",
        "data": {
            "actionName": "gofishing",
            "actionCode": 1,
            "result": result == "successfully",
            "gameTime": "12:23:10",
            "msg": f"Went fishing {reason_map[result]}."
        }
    }

@tool
def mine() -> dict:
    time_consumed = random.uniform(0.1, 1.0)
    time.sleep(time_consumed)
    """Mine for resources, costing energy.
    
    Constraints:
        - Must have enough energy.
        - Must be in the mine.
    
    Returns:
        dict: A simulated response indicating the success of the mining action.
    """
    result = random.choice(["successfully", "unsuccessfully"])
    reason_map = {
        "successfully": "mined resources successfully",
        "unsuccessfully": "failed to mine resources because you don't have enough energy or you are not in the mine"
    }
    return {
        "characterId": 1,
        "messageCode": 3,
        "messageName": "actionresult",
        "data": {
            "actionName": "mine",
            "actionCode": 1,
            "result": result == "successfully",
            "gameTime": "12:23:10",
            "msg": f"Mined resources {reason_map[result]}."
        }
    }

@tool
def harvest() -> dict:
    """Harvest crops, costing energy.
    
    Constraints:
        - Must have enough energy.
        - Must be in the harvest area.
    
    Returns:
        dict: A simulated response indicating the success of the harvesting action.
    """
    time_consumed = random.uniform(0.1, 1.0)
    time.sleep(time_consumed)
    result = random.choice(["successfully", "unsuccessfully"])
    reason_map = {
        "successfully": "harvested crops successfully",
        "unsuccessfully": "failed to harvest crops because you don't have enough energy or you are not in the harvest area"
    }
    return {
        "characterId": 1,
        "messageCode": 3,
        "messageName": "actionresult",
        "data": {
            "actionName": "harvest",
            "actionCode": 1,
            "result": result == "successfully",
            "gameTime": "12:23:10",
            "msg": f"Harvested crops {reason_map[result]}."
        }
    }

@tool
def buy(itemType: str, amount: int) -> dict:
    """Purchase items, costing money.
    
    Args:
        itemType (str): The type of item to purchase. Must be one of (Ore, Bread, Apple, Wheat, Fish).
        amount (int): The amount of the item to purchase.
    
    Constraints:
        - Must have enough money.
        - Items must be available in sufficient quantity in the AMM.
    
    Returns:
        dict: A simulated response indicating the success of the purchase action.
    """
    time_consumed = random.uniform(0.1, 1.0)
    time.sleep(time_consumed)
    result = random.choice(["successfully", "unsuccessfully"])
    reason_map = {
        "successfully": "purchased items successfully",
        "unsuccessfully": "failed to purchase items because you don't have enough money or the items are not available in sufficient quantity in the AMM"
    }
    return {
        "characterId": 1,
        "messageCode": 3,
        "messageName": "actionresult",
        "data": {
            "actionName": "buy",
            "actionCode": 1,
            "result": result == "successfully",
            "gameTime": "12:23:10",
            "msg": f"Purchased {amount} of {itemType} {reason_map[result]}."
        }
    }

@tool
def sell(itemType: str, amount: int) -> dict:
    """Sell items for money.
    
    Args:
        itemType (str): The type of item to sell. Must be one of (Ore, Bread, Apple, Wheat, Fish).
        amount (int): The amount of the item to sell.
    
    Constraints:
        - Must have enough items in inventory.
    
    Returns:
        dict: A simulated response indicating the success of the selling action.
    """
    time_consumed = random.uniform(0.1, 1.0)
    time.sleep(time_consumed)
    result = random.choice(["successfully", "unsuccessfully"])
    reason_map = {
        "successfully": "sold items successfully",
        "unsuccessfully": "failed to sell items because you don't have enough items in inventory"
    }
    return {
        "characterId": 1,
        "messageCode": 3,
        "messageName": "actionresult",
        "data": {
            "actionName": "sell",
            "actionCode": 1,
            "result": result == "successfully",
            "gameTime": "12:23:10",
            "msg": f"Sold {amount} of {itemType} {reason_map[result]}."
        }
    }

@tool
def use_item(itemType: str, amount: int) -> dict:
    """Use an item.
    
    Args:
        itemType (str): The type of item to use. Must be one of (Ore, Bread, Apple, Wheat, Fish).
        amount (int): The amount of the item to use.
    
    Constraints:
        - Must have enough items in inventory.
    
    Returns:
        dict: A simulated response indicating the success of the item usage action.
    """
    time_consumed = random.uniform(0.1, 1.0)
    time.sleep(time_consumed)
    result = random.choice(["successfully", "unsuccessfully"])
    reason_map = {
        "successfully": "used items successfully",
        "unsuccessfully": "failed to use items because you don't have enough items in inventory"
    }
    return {
        "characterId": 1,
        "messageCode": 3,
        "messageName": "actionresult",
        "data": {
            "actionName": "use_item",
            "actionCode": 1,
            "result": result == "successfully",
            "gameTime": "12:23:10",
            "msg": f"Used {amount} of {itemType} {reason_map[result]}."
        }
    }

@tool
def see_doctor(hours: int) -> dict:
    """Visit a doctor, costing money.
    
    Args:
        hours (int): The number of hours to visit the doctor.
    
    Constraints:
        - Must have enough money.
        - Must be in the hospital.
    
    Returns:
        dict: A simulated response indicating the success of the doctor visit.
    """
    time_consumed = random.uniform(0.1, 1.0)
    time.sleep(time_consumed)
    result = random.choice(["successfully", "unsuccessfully"])
    reason_map = {
        "successfully": "visited doctor successfully",
        "unsuccessfully": "failed to visit doctor because you don't have enough money or you are not in the hospital"
    }
    return {
        "characterId": 1,
        "messageCode": 3,
        "messageName": "actionresult",
        "data": {
            "actionName": "see_doctor",
            "actionCode": 1,
            "result": result == "successfully",
            "gameTime": "12:23:10",
            "msg": f"Visited doctor for {hours} hours {reason_map[result]}."
        }
    }

@tool
def sleep(hours: int) -> dict:
    """Sleep to recover energy and health.
    
    Args:
        hours (int): The number of hours to sleep.
    
    Constraints:
        - Must be at home.
    
    Returns:
        dict: A simulated response indicating the success of the sleep action.
    """
    time_consumed = random.uniform(0.1, 1.0)
    time.sleep(time_consumed)
    result = random.choice(["successfully", "unsuccessfully"])
    reason_map = {
        "successfully": f"slept for {hours} hours successfully",
        "unsuccessfully": "failed to sleep because you are not at home"
    }
    return {
        "characterId": 1,
        "messageCode": 3,
        "messageName": "actionresult",
        "data": {
            "actionName": "sleep",
            "actionCode": 1,
            "result": result == "successfully",
            "gameTime": "12:23:10",
            "msg": f"Slept for {hours} hours {reason_map[result]}."
        }
    }

@tool
def study(hours: int) -> dict:
    """Study to achieve a higher degree.
    
    Args:
        hours (int): The number of hours to study.
    
    Constraints:
        - Must be in school.
        - Must have enough money.
    
    Returns:
        dict: A simulated response indicating the success of the study action.
    """
    time_consumed = random.uniform(0.1, 1.0)
    time.sleep(time_consumed)
    result = random.choice(["successfully", "unsuccessfully"])
    reason_map = {
        "successfully": f"studied for {hours} hours successfully",
        "unsuccessfully": "failed to study because you are not in school or you don't have enough money"
    }
    return {
        "characterId": 1,
        "messageCode": 3,
        "messageName": "actionresult",
        "data": {
            "actionName": "study",
            "actionCode": 1,
            "result": result == "successfully",
            "gameTime": "12:23:10",
            "msg": f"Studied for {hours} hours {reason_map[result]}."
        }
    }

@tool
def nav(placeName: str) -> dict:
    """Navigate to a specified location.
    
    Args:
        placeName (str): The name of the place to navigate to. Must be one of (school, workshop, home, farm, mall, square, hospital, fruit, harvest, fishing, mine, orchard).
    
    Returns:
        dict: A simulated response indicating the success of the navigation action.
    """
    time_consumed = random.uniform(0.1, 1.0)
    time.sleep(time_consumed)
    result = random.choice(["successfully", "unsuccessfully"])
    reason_map = {
        "successfully": f"navigated to {placeName} successfully",
        "unsuccessfully": f"failed to navigate to {placeName} because you are not in the correct location"
    }

    return {
        "characterId": 1,
        "messageCode": 3,
        "messageName": "actionresult",
        "data": {
            "actionName": "nav",
            "actionCode": 1,
            "result": result == "successfully",
            "gameTime": "12:23:10",
            "msg": f"Navigated to {placeName} {reason_map[result]}."
        }
    }
