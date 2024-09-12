from langchain_core.tools import tool
import requests


BASE_URL = "http://localhost:8000"


def _make_api_call(endpoint: str, data: dict, method: str = "post") -> dict:
    """Make an API call to the specified endpoint.

    Args:
        endpoint (str): API endpoint
        data (dict): Request payload
        method (str): HTTP request method, default is "post"

    Returns:
        dict: JSON data from the API response
    """
    url = f"{BASE_URL}/{endpoint}"
    if method.lower() == "get":
        response = requests.get(url, params=data)
    else:
        response = requests.post(url, json=data)
    return response.json()


@tool
def do_freelance_job(
    timelength: int, merchantid: int = None, method: str = "post"
) -> dict:
    """Perform freelance work for a specified duration.

    Args:
        timelength (int): Duration of work in hours
        merchantid (int, optional): Merchant ID
        method (str): HTTP method to use (get or post)

    Returns:
        dict: API response data
    """
    return _make_api_call(
        "freelance-job", {"timelength": timelength, "merchantid": merchantid}, method
    )


@tool
def navigate_to(to: str, method: str = "post") -> dict:
    """Navigate to a specified location.

    Args:
        to (str): Target location
        method (str): HTTP method to use (get or post)

    Returns:
        dict: API response data
    """
    return _make_api_call("go-to", {"to": to}, method)


@tool
def sleep(timelength: int, method: str = "post") -> dict:
    """Sleep for a specified duration.

    Args:
        timelength (int): Duration of sleep in hours
        method (str): HTTP method to use (get or post)

    Returns:
        dict: API response data
    """
    return _make_api_call("sleep", {"timelength": timelength}, method)


@tool
def work_change(jobid: int, method: str = "post") -> dict:
    """Change the character's job.

    Args:
        jobid (int): New job ID
        method (str): HTTP method to use (get or post)

    Returns:
        dict: API response data
    """
    return _make_api_call("work-change", {"jobid": jobid}, method)


@tool
def get_character_stats(method: str = "get") -> dict:
    """Get character statistics.

    Args:
        method (str): HTTP method to use (get or post)

    Returns:
        dict: API response data
    """
    return _make_api_call("character/data", {}, method)


@tool
def get_character_status(method: str = "get") -> dict:
    """Get character status information.

    Args:
        method (str): HTTP method to use (get or post)

    Returns:
        dict: API response data
    """
    return _make_api_call("character/status", {}, method)


@tool
def get_character_basic_info(method: str = "get") -> dict:
    """Get character basic information.

    Args:
        method (str): HTTP method to use (get or post)

    Returns:
        dict: API response data
    """
    return _make_api_call("character/bsinfo", {}, method)


@tool
def get_inventory(method: str = "get") -> dict:
    """Get character inventory information.

    Args:
        method (str): HTTP method to use (get or post)

    Returns:
        dict: API response data
    """
    return _make_api_call("character/inventory", {}, method)


@tool
def submit_resume(jobid: int, cvurl: str, method: str = "post") -> dict:
    """Submit a resume.

    Args:
        jobid (int): Job ID
        cvurl (str): Resume URL
        method (str): HTTP method to use (get or post)

    Returns:
        dict: API response data
    """
    return _make_api_call("resume-submission", {"jobid": jobid, "cvurl": cvurl}, method)


@tool
def vote(userid: str, method: str = "post") -> dict:
    """Cast a vote.

    Args:
        userid (str): User ID
        method (str): HTTP method to use (get or post)

    Returns:
        dict: API response data
    """
    return _make_api_call("vote", {"userid": userid}, method)


@tool
def do_public_job(jobid: int, timelength: int, method: str = "post") -> dict:
    """Perform a public job.

    Args:
        jobid (int): Job ID
        timelength (int): Duration of work in hours
        method (str): HTTP method to use (get or post)

    Returns:
        dict: API response data
    """
    return _make_api_call(
        "public-job", {"jobid": jobid, "timelength": timelength}, method
    )


@tool
def study(timelength: int, method: str = "post") -> dict:
    """Study for a specified duration.

    Args:
        timelength (int): Duration of study in hours
        method (str): HTTP method to use (get or post)

    Returns:
        dict: API response data
    """
    return _make_api_call("study", {"timelength": timelength}, method)


@tool
def talk(
    userid: str, talkcontent: str, talkid: str = None, method: str = "post"
) -> dict:
    """Start or continue a conversation.

    Args:
        userid (str): User ID
        talkcontent (str): Content of the talk
        talkid (str, optional): Talk ID for existing conversations
        method (str): HTTP method to use (get or post)

    Returns:
        dict: API response data
    """
    data = {"userid": userid, "talkcontent": talkcontent}
    if talkid:
        data["talkid"] = talkid
    return _make_api_call("talk", data, method)


@tool
def end_talk(userid: str, talkid: str, method: str = "post") -> dict:
    """End a conversation.

    Args:
        userid (str): User ID
        talkid (str): Talk ID
        method (str): HTTP method to use (get or post)

    Returns:
        dict: API response data
    """
    return _make_api_call("end-talk", {"userid": userid, "talkid": talkid}, method)


@tool
def calculate_distance(to: str, method: str = "post") -> dict:
    """Calculate distance to a destination.

    Args:
        to (str): Destination
        method (str): HTTP method to use (get or post)

    Returns:
        dict: API response data
    """
    return _make_api_call("distance", {"to": to}, method)


@tool
def trade(
    merchantid: int, merchantnum: int, transactiontype: int, method: str = "post"
) -> dict:
    """Perform a trade transaction.

    Args:
        merchantid (int): Merchant ID
        merchantnum (int): Number of items to trade
        transactiontype (int): Type of transaction (0 for buy, 1 for sell)
        method (str): HTTP method to use (get or post)

    Returns:
        dict: API response data
    """
    return _make_api_call(
        "trade",
        {
            "merchantid": merchantid,
            "merchantnum": merchantnum,
            "transactiontype": transactiontype,
        },
        method,
    )


@tool
def use_item(merchantid: int, merchantnum: int = 1, method: str = "post") -> dict:
    """Use an item from the inventory.

    Args:
        merchantid (int): Merchant ID of the item
        merchantnum (int, optional): Number of items to use, default is 1
        method (str): HTTP method to use (get or post)

    Returns:
        dict: API response data
    """
    return _make_api_call(
        "use", {"merchantid": merchantid, "merchantnum": merchantnum}, method
    )


@tool
def see_doctor(method: str = "post") -> dict:
    """Visit a doctor to improve health.

    Args:
        method (str): HTTP method to use (get or post)

    Returns:
        dict: API response data
    """
    return _make_api_call("see-doctor", {}, method)


@tool
def get_freelance_jobs(jobid: int = None, method: str = "get") -> dict:
    """Get available freelance jobs.

    Args:
        jobid (int, optional): Specific job ID to retrieve
        method (str): HTTP method to use (get or post)

    Returns:
        dict: API response data
    """
    params = {}
    if jobid is not None:
        params["jobid"] = jobid
    return _make_api_call("freelance-jobs", params, method)


@tool
def get_public_jobs(jobid: int = None, method: str = "get") -> dict:
    """Get available public jobs.

    Args:
        jobid (int, optional): Specific job ID to retrieve
        method (str): HTTP method to use (get or post)

    Returns:
        dict: API response data
    """
    params = {}
    if jobid is not None:
        params["jobid"] = jobid
    return _make_api_call("public-jobs", params, method)


@tool
def get_candidates(method: str = "get") -> dict:
    """Get candidate information for the current week's voting.

    Args:
        method (str): HTTP method to use (get or post)

    Returns:
        dict: API response data
    """
    return _make_api_call("candidates", {}, method)


@tool
def get_activity_subjects(subjectid: int = None, method: str = "get") -> dict:
    """Get activity subjects.

    Args:
        subjectid (int, optional): Specific subject ID to retrieve
        method (str): HTTP method to use (get or post)

    Returns:
        dict: API response data
    """
    params = {}
    if subjectid is not None:
        params["subjectid"] = subjectid
    return _make_api_call("activity", params, method)


@tool
def get_talk_data(talkid: str, method: str = "get") -> dict:
    """Get data for a specific talk.

    Args:
        talkid (str): Talk ID
        method (str): HTTP method to use (get or post)

    Returns:
        dict: API response data
    """
    return _make_api_call("talk_data", {"talkid": talkid}, method)


@tool
def get_position(
    coordinate: str = None, positionid: str = None, method: str = "get"
) -> dict:
    """Get position information.

    Args:
        coordinate (str, optional): Coordinate to search
        positionid (str, optional): Position ID to search
        method (str): HTTP method to use (get or post)

    Returns:
        dict: API response data
    """
    params = {}
    if coordinate:
        params["coordinate"] = coordinate
    if positionid:
        params["positionid"] = positionid
    return _make_api_call("position", params, method)


# print(do_freelance_job.invoke({"timelength": 2, "merchantid": 1}))
# print(navigate_to.invoke({"to": "商店"}))
# print(sleep.invoke({"timelength": 8}))
# print(work_change.invoke({"jobid": 1}))
# print(get_character_stats.invoke({}))
# print(get_character_status.invoke({}))
# print(get_character_basic_info.invoke({}))
# print(get_inventory.invoke({}))
# print(submit_resume.invoke({"jobid": 1, "cvurl": "http://example.com/cv"}))
# print(vote.invoke({"userid": "user123"}))
# print(do_public_job.invoke({"jobid": 1, "timelength": 4}))
# print(study.invoke({"timelength": 2}))
# print(talk.invoke({"userid": "user456", "talkcontent": "你好！"}))
# print(end_talk.invoke({"userid": "user456", "talkid": "1234abcd"}))
# print(get_activity_subjects.invoke({}))
# print(get_talk_data.invoke({"talkid": "1234abcd"}))
# print(get_position.invoke({}))
# print(get_candidates.invoke({}))
