# from langchain_core.tools import tool
# import requests


# BASE_URL = "http://localhost:8000"


# def _make_api_call(endpoint: str, data: dict, method: str = "post") -> dict:
#     """Make an API call to the specified endpoint.

#     Args:
#         endpoint (str): API endpoint
#         data (dict): Request payload
#         method (str): HTTP request method, default is "post"

#     Returns:
#         dict: JSON data from the API response
#     """
#     url = f"{BASE_URL}/{endpoint}"
#     if method.lower() == "get":
#         response = requests.get(url, params=data)
#     elif method.lower() == "post":
#         response = requests.post(url, json=data)
#     else:
#         raise ValueError(f"Unsupported HTTP method: {method}")
#     return response.json()


# @tool
# def do_freelance_job(
#     timelength: int, merchantid: int = None, method: str = "post"
# ) -> dict:
#     """Perform freelance work for a specified duration.

#     Args:
#         timelength (int): Duration of work in hours
#         merchantid (int, optional): Merchant ID
#         method (str): HTTP method to use (get or post)

#     Returns:
#         dict: API response data
#     """
#     return _make_api_call(
#         "freelance-job", {"timelength": timelength, "merchantid": merchantid}, method
#     )


# @tool
# def navigate_to(to: str, method: str = "post") -> dict:
#     """Navigate to a specified location.

#     Args:
#         to (str): Target location
#         method (str): HTTP method to use (get or post)

#     Returns:
#         dict: API response data
#     """
#     return _make_api_call("go-to", {"to": to}, method)


# @tool
# def sleep(timelength: int, method: str = "post") -> dict:
#     """Sleep for a specified duration.

#     Args:
#         timelength (int): Duration of sleep in hours
#         method (str): HTTP method to use (get or post)

#     Returns:
#         dict: API response data
#     """
#     return _make_api_call("sleep", {"timelength": timelength}, method)


# @tool
# def work_change(jobid: int, method: str = "post") -> dict:
#     """Change the character's job.

#     Args:
#         jobid (int): New job ID
#         method (str): HTTP method to use (get or post)

#     Returns:
#         dict: API response data
#     """
#     return _make_api_call("work-change", {"jobid": jobid}, method)


# @tool
# def get_character_stats(method: str = "get") -> dict:
#     """Get character statistics.

#     Args:
#         method (str): HTTP method to use (get or post)

#     Returns:
#         dict: API response data
#     """
#     return _make_api_call("character/data", {}, method)


# @tool
# def get_character_status(method: str = "get") -> dict:
#     """Get character status information.

#     Args:
#         method (str): HTTP method to use (get or post)

#     Returns:
#         dict: API response data
#     """
#     return _make_api_call("character/status", {}, method)


# @tool
# def get_character_basic_info(method: str = "get") -> dict:
#     """Get character basic information.

#     Args:
#         method (str): HTTP method to use (get or post)

#     Returns:
#         dict: API response data
#     """
#     return _make_api_call("character/bsinfo", {}, method)


# @tool
# def get_inventory(method: str = "get") -> dict:
#     """Get character inventory information.

#     Args:
#         method (str): HTTP method to use (get or post)

#     Returns:
#         dict: API response data
#     """
#     return _make_api_call("character/inventory", {}, method)


# @tool
# def submit_resume(jobid: int, cvurl: str, method: str = "post") -> dict:
#     """Submit a resume.

#     Args:
#         jobid (int): Job ID
#         cvurl (str): Resume URL
#         method (str): HTTP method to use (get or post)

#     Returns:
#         dict: API response data
#     """
#     return _make_api_call("resume-submission", {"jobid": jobid, "cvurl": cvurl}, method)


# @tool
# def vote(userid: str, method: str = "post") -> dict:
#     """Cast a vote.

#     Args:
#         userid (str): User ID
#         method (str): HTTP method to use (get or post)

#     Returns:
#         dict: API response data
#     """
#     return _make_api_call("vote", {"userid": userid}, method)


# @tool
# def do_public_job(jobid: int, timelength: int, method: str = "post") -> dict:
#     """Perform a public job.

#     Args:
#         jobid (int): Job ID
#         timelength (int): Duration of work in hours
#         method (str): HTTP method to use (get or post)

#     Returns:
#         dict: API response data
#     """
#     return _make_api_call(
#         "public-job", {"jobid": jobid, "timelength": timelength}, method
#     )


# @tool
# def study(timelength: int, method: str = "post") -> dict:
#     """Study for a specified duration.

#     Args:
#         timelength (int): Duration of study in hours
#         method (str): HTTP method to use (get or post)

#     Returns:
#         dict: API response data
#     """
#     return _make_api_call("study", {"timelength": timelength}, method)


# @tool
# def talk(
#     userid: str, talkcontent: str, talkid: str = None, method: str = "post"
# ) -> dict:
#     """Start or continue a conversation.

#     Args:
#         userid (str): User ID
#         talkcontent (str): Content of the talk
#         talkid (str, optional): Talk ID for existing conversations
#         method (str): HTTP method to use (get or post)

#     Returns:
#         dict: API response data
#     """
#     data = {"userid": userid, "talkcontent": talkcontent}
#     if talkid:
#         data["talkid"] = talkid
#     return _make_api_call("talk", data, method)


# @tool
# def end_talk(userid: str, talkid: str, method: str = "post") -> dict:
#     """End a conversation.

#     Args:
#         userid (str): User ID
#         talkid (str): Talk ID
#         method (str): HTTP method to use (get or post)

#     Returns:
#         dict: API response data
#     """
#     return _make_api_call("end-talk", {"userid": userid, "talkid": talkid}, method)


# @tool
# def calculate_distance(to: str, method: str = "post") -> dict:
#     """Calculate distance to a destination.

#     Args:
#         to (str): Destination
#         method (str): HTTP method to use (get or post)

#     Returns:
#         dict: API response data
#     """
#     return _make_api_call("distance", {"to": to}, method)


# @tool
# def trade(
#     merchantid: int, merchantnum: int, transactiontype: int, method: str = "post"
# ) -> dict:
#     """Perform a trade transaction.

#     Args:
#         merchantid (int): Merchant ID
#         merchantnum (int): Number of items to trade
#         transactiontype (int): Type of transaction (0 for buy, 1 for sell)
#         method (str): HTTP method to use (get or post)

#     Returns:
#         dict: API response data
#     """
#     return _make_api_call(
#         "trade",
#         {
#             "merchantid": merchantid,
#             "merchantnum": merchantnum,
#             "transactiontype": transactiontype,
#         },
#         method,
#     )


# @tool
# def use_item(merchantid: int, merchantnum: int = 1, method: str = "post") -> dict:
#     """Use an item from the inventory.

#     Args:
#         merchantid (int): Merchant ID of the item
#         merchantnum (int, optional): Number of items to use, default is 1
#         method (str): HTTP method to use (get or post)

#     Returns:
#         dict: API response data
#     """
#     return _make_api_call(
#         "use", {"merchantid": merchantid, "merchantnum": merchantnum}, method
#     )


# @tool
# def see_doctor(method: str = "post") -> dict:
#     """Visit a doctor to improve health.

#     Args:
#         method (str): HTTP method to use (get or post)

#     Returns:
#         dict: API response data
#     """
#     return _make_api_call("see-doctor", {}, method)


# @tool
# def get_freelance_jobs(jobid: int = None, method: str = "get") -> dict:
#     """Get available freelance jobs.

#     Args:
#         jobid (int, optional): Specific job ID to retrieve
#         method (str): HTTP method to use (get or post)

#     Returns:
#         dict: API response data
#     """
#     params = {}
#     if jobid is not None:
#         params["jobid"] = jobid
#     return _make_api_call("freelance-jobs", params, method)


# @tool
# def get_public_jobs(jobid: int = None, method: str = "get") -> dict:
#     """Get available public jobs.

#     Args:
#         jobid (int, optional): Specific job ID to retrieve
#         method (str): HTTP method to use (get or post)

#     Returns:
#         dict: API response data
#     """
#     params = {}
#     if jobid is not None:
#         params["jobid"] = jobid
#     return _make_api_call("public-jobs", params, method)


# @tool
# def get_candidates(method: str = "get") -> dict:
#     """Get candidate information for the current week's voting.

#     Args:
#         method (str): HTTP method to use (get or post)

#     Returns:
#         dict: API response data
#     """
#     return _make_api_call("candidates", {}, method)


# @tool
# def get_activity_subjects(subjectid: int = None, method: str = "get") -> dict:
#     """Get activity subjects.

#     Args:
#         subjectid (int, optional): Specific subject ID to retrieve
#         method (str): HTTP method to use (get or post)

#     Returns:
#         dict: API response data
#     """
#     params = {}
#     if subjectid is not None:
#         params["subjectid"] = subjectid
#     return _make_api_call("activity", params, method)


# @tool
# def get_talk_data(talkid: str, method: str = "get") -> dict:
#     """Get data for a specific talk.

#     Args:
#         talkid (str): Talk ID
#         method (str): HTTP method to use (get or post)

#     Returns:
#         dict: API response data
#     """
#     return _make_api_call("talk_data", {"talkid": talkid}, method)


# @tool
# def get_position(
#     coordinate: str = None, positionid: str = None, method: str = "get"
# ) -> dict:
#     """Get position information.

#     Args:
#         coordinate (str, optional): Coordinate to search
#         positionid (str, optional): Position ID to search
#         method (str): HTTP method to use (get or post)

#     Returns:
#         dict: API response data
#     """
#     params = {}
#     if coordinate:
#         params["coordinate"] = coordinate
#     if positionid:
#         params["positionid"] = positionid
#     return _make_api_call("position", params, method)

# @tool
# def eat(timelength: int, method: str = "post") -> dict:
#     """Eat something.

#     Args:
#         method (str): HTTP method to use (get or post)

#     Returns:
#         dict: API response data
#     """
#     return _make_api_call("eat", {"timelength": timelength}, method)



#sample response:
#{
#     characterId : 1,
#     messageCode : 3,
#     messageName : "actionresult" ,
#     data:
#     {
#         actionName : "pickapple"
#         actionCode : 1,
#         result : true,
#         gameTime : "12:23:10"
#         msg : "pickapple successfully"
#     }
# }

from langchain_core.tools import tool

@tool
def submit_cv(targetOccupation: str, content: str) -> dict:
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