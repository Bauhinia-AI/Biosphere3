from core.conversation_srv.conversation_model import *
from core.conversation_srv.conversation_prompts import *
from langchain_openai import ChatOpenAI
from loguru import logger
from typing import Literal
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import websockets
import json
import os
import pprint
from core.db.database_api_utils import make_api_request_sync
from core.db.game_api_utils import make_api_request_sync as make_backend_api_request_sync
from datetime import datetime, timedelta
import random
import numpy as np


logger.add(
        "conversation_engines.log",
        format="{time} {level} {message}",
    )

conversation_topic_planner = conversation_topic_planner_prompt | ChatOpenAI(
    base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini", temperature=1.
).with_structured_output(ConversationTopics)

conversation_planner = conversation_planner_prompt | ChatOpenAI(
    base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini", temperature=1.
).with_structured_output(PreConversationTask)

conversation_check = conversation_check_prompt | ChatOpenAI(
    base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini", temperature=0
).with_structured_output(CheckResult)

conversation_responser = conversation_responser_prompt | ChatOpenAI(
    base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini", temperature=1
).with_structured_output(PreResponse)

impression_update = impression_update_prompt | ChatOpenAI(
    base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini", temperature=1
).with_structured_output(ImpressionUpdate)

knowledge_generator = knowledge_generator_prompt | ChatOpenAI(
    base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini", temperature=1
).with_structured_output(Knowledge)

conversation_intimacy_mark = intimacy_mark_prompt | ChatOpenAI(
    base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini", temperature=1.
).with_structured_output(IntimacyMark)


async def generate_daily_conversation_plan(state: ConversationState):
    # process the remaining read-only conversations from the previous day
    if len(state["ongoing_task"]) != 0:
        await handling_readonly_conversation(state)
   # reset the task list
    state["daily_task"] = []

    # update profile
    userid = state["userid"]
    character_data = {"characterId": userid}
    profile = make_api_request_sync("GET", "/characters/", params=character_data)
    state["character_stats"] = profile["data"][0]
    logger.info(f"User {state['userid']}: {profile['message']}")
    logger.info(f"User {state['userid']} current state is: {state['character_stats']}")

    # get new daily objectives
    get_daily_objectives_data = {
        "characterId": state["userid"]
    }
    objective_response = make_api_request_sync("GET", "/decision/", params=get_daily_objectives_data)
    if objective_response["data"] is not None:
        if "daily_objective" in objective_response["data"][0]:
            memory = objective_response["data"][0]["daily_objective"]
        else:
            memory = ["No objectives."]
    else:
        memory = []
    logger.info(f"User {state['userid']} current daily objectives are: {memory}")

    # get character_arc
    arc_response = make_api_request_sync("GET", "/character_arc/with_changes", params={"characterId": state["userid"], "k": 1})
    if not arc_response["data"]:
        arc_data = []
    else:
        arc_data = arc_response["data"]
    logger.info(f"User {state['userid']} current character arc is {arc_data}")

    # get featured prompt (topic)
    topic_response = make_api_request_sync("GET", "/conversation_prompt/", params={"characterId": state["userid"]})
    if not topic_response["data"]:
        topic_requirement = ""
    else:
        topic_requirement = topic_response["data"][0]["topic_requirements"]

    # look up the past conversation topics
    current_day, current_hour, current_minute = calculate_game_time(datetime.now())
    get_conversation_memory_params = {"characterId": state['userid'], "day": current_day-1}
    past_topic_response = make_api_request_sync(
        "GET", "/conversation_memory/", params=get_conversation_memory_params
    )
    if not past_topic_response["data"]:
        past_topics = []
    else:
        past_topics = past_topic_response["data"][0]["topic_plan"]

    # generate conversation topic list
    retry_count = 0
    while retry_count < 3:
        try:
            topic_list = conversation_topic_planner.invoke(
                {
                    "character_stats": state["character_stats"],
                    "memory": memory,
                    "personality": arc_data,
                    "requirements": topic_requirement,
                    "past_topics": past_topics
                }
            )
            break
        except Exception as e:
            logger.error(
                f"⛔ User {state['userid']} Error in generate daily conversation topics: {e}"
            )
            retry_count += 1
            continue
    logger.info(f"Today User {state['userid']} is going to talk with others about: {topic_list['topics']}")

    final_topic_list = topic_list["topics"]
    conversation_plan = DailyConversationPlan(conversations=[])

    # generate conversation time list
    try:
        start_time_list = generate_talk_time(5, state['userid'])
        if not start_time_list:
            raise ValueError("It's too late. I should start socializing next day.")
        elif start_time_list == ["000"]:
            start_time_list = []
            raise ValueError("RUNNING OUT OF POWER!")
    except ValueError as e:
        logger.error(f"⛔ User {state['userid']} Error in planning conversation: {e}")

    logger.info(f"User {state['userid']} planned start time is {start_time_list}")

    plan_topic = []
    plan_time = []
    if start_time_list:
        for index, start_time in enumerate(start_time_list):
            # start_time = start_time_list[index]
            talk = final_topic_list[index]
            # reconstruct the format
            single_conversation = ConversationTask(
                from_id=state["userid"],
                to_id=0,  # talk["userid"],
                start_time=start_time,
                topic=talk,
                Finish=[False, False]
            )
            plan_topic.append(talk)
            plan_time.append(start_time)
            conversation_plan.conversations.append(single_conversation)

        # update daily conversation plan to state
        state["daily_task"] = conversation_plan.conversations

        # update daily conversation plan to database
        current_day, current_hour, current_minute = calculate_game_time(datetime.now())
        get_conversation_memory_params = {"characterId": state["userid"], "day": current_day}
        memory_response = make_api_request_sync(
            "GET", "/conversation_memory/", params=get_conversation_memory_params
        )
        if not memory_response["data"]:
            store_conversation_memory_data = {
                "characterId": state["userid"],
                "day": current_day,
                "topic_plan": plan_topic,
                "time_list": plan_time,
                "started": [],
            }
            memory_store_response = make_api_request_sync(
                "POST", "/conversation_memory/", data=store_conversation_memory_data
            )
            logger.info(f"User {state['userid']} conversation plan stored: {memory_store_response['message']}")
        else:
            old_topic = memory_response["data"][0]["topic_plan"]
            old_time = memory_response["data"][0]["time_list"]
            if not memory_response["data"][0]["started"]:
                point = -1
            else:
                point = old_time.index(memory_response["data"][0]["started"][-1]["time"])
            update_conversation_memory_data = {
                "characterId": state["userid"],
                "day": current_day,
                "update_fields": {
                    "topic_plan": old_topic[0:point+1]+plan_topic,
                    "time_list": old_time[0:point+1]+plan_time
                }
            }
            memory_update_response = make_api_request_sync(
                "PUT", "/conversation_memory/", data=update_conversation_memory_data
            )
            logger.info(f"User {state['userid']} conversation plan updated: {memory_update_response['message']}")

        logger.info(f"🧠 NEW CONVERSATION PLAN GENERATED...")
        logger.info(f"New conversation plan of User {state['userid']}: {state['daily_task']}")
    return state


def create_message(character_id, message_name, conversation: RunningConversation, message_code=100):  #messagecode=100 for conversation system
    return {
        "characterId": character_id,
        "messageCode": message_code,
        "messageName": message_name,
        "data": conversation,
    }


# send message through ws
async def send_conversation_message(state: ConversationState, conversation: RunningConversation):
    websocket = state["websocket"]
    if websocket is None or websocket.closed:
        logger.error(f"⛔ User {state['userid']}: WebSocket is not connected.")
        return
    try:
        message = create_message(
            character_id=state["userid"],
            message_name="to_agent",
            conversation=conversation
        )
        await websocket.send(json.dumps(message))
        logger.info(f"📤 User {state['userid']}: Sent a response message: {message}")
    except websockets.ConnectionClosed:
        logger.warning(f"User {state['userid']}: WebSocket connection closed during send.")
    except Exception as e:
        logger.error(f"User {state['userid']}: Error sending message: {e}")


async def start_conversation(state: ConversationState):
    current_talk = state["daily_task"][0]  # waiting for check
    logger.info(f"User {state['userid']}: current conversation task is {current_talk}.")
    game_start_time = current_talk["start_time"]
    time_obj = datetime.strptime(game_start_time, "%H:%M")
    start_hour = time_obj.hour
    start_minute = time_obj.minute
    current_time = calculate_game_time(datetime.now())
    if current_time[1] < start_hour or (current_time[1] == start_hour and current_time[2] < start_minute):
        sleep_time = ((-current_time[1]+start_hour)*60*60 + (-current_time[2]+start_minute)*60)//7
        logger.info(f"User {state['userid']}: next conversation will be started after {sleep_time} seconds.")
        await asyncio.sleep(sleep_time-5)  
    else:
        logger.info(f"User {state['userid']} missed one conversation. Start this task right now...")
        current_talk['start_time'] = f"{current_time[1]:02}"+":"+f"{current_time[2]:02}"

    # get profile
    userid = state["userid"]
    character_data = {"characterId": userid}
    profile = make_api_request_sync("GET", "/characters/", params=character_data)
    state["character_stats"] = profile["data"][0]
    logger.info(f"User {state['userid']}: {profile['message']}")
    logger.info(f"User {state['userid']} current state is: {state['character_stats']}")

    # get conversations that have already happened
    talked_data = {
        "characterId": state["userid"],
        "day": current_time[0]
    }
    talked_response = make_api_request_sync("GET", "/conversation_memory/", params=talked_data)
    talked = talked_response["data"][0]["started"]

    logger.info(f"🧠 CHECKING WHETHER TO START THE CONVERSATION ...")

    # check whether to start this task
    retry_count = 0
    while retry_count < 3:
        try:
            check_response = conversation_check.invoke(
                {
                    "profile": state['character_stats'],
                    "current_talk": current_talk,
                    "finished_talk": talked
                }
            )  
            break
        except Exception as e:
            logger.error(
                f"⛔ User {state['userid']} Error in check conversation: {e}"
            )
            retry_count += 1
            continue

    # only go through the following process when the conversation is checked to be necessary
    if check_response["Need"]:
        # determine who to talk by rag
        encounter_data = {
                    "from_id": state["userid"],
                    "k": 10
                }
        encounter_response = make_api_request_sync("GET", "/encounter_count/by_from_id", params=encounter_data)

        candidate_list = []
        for item in encounter_response["data"]:
            if item["count"] != 0:
                candidate_list.append(item['to_id'])
        logger.info(f"User {state['userid']} candidate list for this conversation is {candidate_list}")

        if not candidate_list:
            character_rag_data = {
                "characterId": state["userid"],
                "topic": current_talk["topic"],
                "k": 2
            }
            rag_response = make_api_request_sync("GET", "/characters/rag", params=character_rag_data)
        else:
            character_rag_data = {
                "characterId": state["userid"],
                "characterList": candidate_list,
                "topic": current_talk["topic"],
                "k": 2
            }
            rag_response = make_api_request_sync("POST", "/characters/rag_in_list", data=character_rag_data)

        current_topic_list = {}
        if not rag_response['data']:
            logger.info(f"User {state['userid']}: There is no suitable person to talk to on this topic {current_talk['topic']}. Randomly choose one.")
            id_data = random_user_with_power(5, state['userid'])
            rag_response["data"] = [{"characterId": id_data}]

        for user in rag_response["data"]:
            if user["characterId"] != state["userid"]:  # never talk to oneself
                logger.info(f"User {state['userid']} plans to talk to {user['characterId']} on this topic.")
                # check character power
                id_data = user["characterId"]
                endpoint = "/characterPower/getByCharacterId/" + str(id_data)
                power_check = make_backend_api_request_sync("GET", endpoint=endpoint)
                if not power_check["data"]:
                    to_id = random_user_with_power(5, state['userid'])
                    logger.info(f"User {user['characterId']} is running out of power, choose another player to talk.")
                elif power_check["data"]["currentPower"] < 5:
                    to_id = random_user_with_power(5, state['userid'])
                    logger.info(f"User {user['characterId']} current power is not enough for a whole conversation, choose another player to talk.")
                else:
                    to_id = user["characterId"]
                logger.info(f"User {state['userid']} finally decided to talk with {to_id} on this topic.")
                impression_query_data = {
                    "from_id": state["userid"],
                    "to_id": to_id,
                    "k": 1
                }
                impression_response = make_api_request_sync("GET", "/impressions/", params=impression_query_data)

                if impression_response["data"]:
                    current_impression = impression_response["data"][0]
                else:
                    current_impression = []
                logger.info(f"The impression from User {state['userid']} to User {to_id} is {current_impression}.")
                current_topic_list = {
                    "topic": current_talk['topic'],
                    "userid": to_id,
                    "impression": current_impression
                }
                break

        # get character_arc
        arc_response = make_api_request_sync("GET", "/character_arc/with_changes", params={"characterId": state["userid"], "k": 1})
        if not arc_response["data"]:
            arc_data = []
        else:
            arc_data = arc_response["data"]
        logger.info(f"User {state['userid']} current character arc is {arc_data}")

        # how to start the conversation
        retry_count = 0
        while retry_count < 3:
            try:
                pre_single_conversation = conversation_planner.invoke(
                    {
                        "character_stats": state["character_stats"],
                        "topic_list": current_topic_list,
                        "personality": arc_data
                    }
                )
                break
            except Exception as e:
                logger.error(
                    f"⛔ User {state['userid']} Error in starting a conversation: {e}"
                )
                retry_count += 1
                continue

        current_realtime = datetime.now()
        current_day, current_hour, current_minute = calculate_game_time(current_realtime)
        send_gametime = [current_day, f"{current_hour:02}" + ":" + f"{current_minute:02}"]
        send_realtime = f"{current_realtime.year}-{current_realtime.month}-{current_realtime.day} {current_realtime.hour}:{current_realtime.minute:02}"
        talk_message = RunningConversation(
            from_id=current_talk["from_id"],
            to_id=current_topic_list["userid"],
            start_time=current_talk["start_time"],
            latest_message={state["character_stats"]["characterName"]: pre_single_conversation["first_sentence"]},
            send_gametime=send_gametime,
            send_realtime=send_realtime,
            Finish=[False, False]
        )
        logger.info(f"User {state['userid']}: to start a conversation {talk_message}.")

        # send message
        await send_conversation_message(state, talk_message)

        logger.info(f"The conversation FROM {current_talk['from_id']} at GAME TIME {current_talk['start_time']} on topic {current_talk['topic']} has started.")

        # store the message to database
        store_conversation_data = {
            "from_id": current_talk["from_id"],
            "to_id": current_topic_list["userid"],
            "start_time": current_talk["start_time"],
            "start_day": current_day,
            "message": pre_single_conversation["first_sentence"],
            "send_gametime": send_gametime,
            "send_realtime": send_realtime,
        }
        store_response = make_api_request_sync("POST", "/conversation/", data=store_conversation_data)
        logger.info(f"User {state['userid']} conversation message stored: {store_response['message']}")

        # update the daily conversation plan
        add_started_data = {
            "characterId": state['userid'],
            "day": current_day,
            "add_started": {"time": current_talk["start_time"], "topic": current_talk["topic"]},
        }
        start_add_response = make_api_request_sync(
            "PUT", "/conversation_memory/", data=add_started_data
        )
        logger.info(f"User {state['userid']} conversation memory added: {start_add_response['message']}")
    else:
        logger.info(f"The conversation FROM {current_talk['from_id']} at GAME TIME {current_talk['start_time']} on topic {current_talk['topic']} is canceled after check.")

    # update the daily_task list
    if len(state["daily_task"]) > 1:
        state["daily_task"] = state["daily_task"][1:]
    else:
        state["daily_task"] = []

    return state


# reply the message
async def generate_response(state: ConversationState):
    question_item = await state["waiting_response"].get()

    if question_item is None:
        logger.error(f"User {state['userid']}: No conversation is waiting for reply.")
    logger.info(f"User {state['userid']}: is replying the message: {question_item}")
    logger.info(f"🧠 GENERATING RESPONSE...")

    # update profile
    userid = state["userid"]
    character_data = {"characterId": userid}
    profile = make_api_request_sync("GET", "/characters/", params=character_data)
    state["character_stats"] = profile["data"][0]
    logger.info(f"User {state['userid']}: {profile['message']}")
    logger.info(f"User {state['userid']} current state is: {state['character_stats']}")

    question = question_item["latest_message"]

    # get the history for this conversation event
    history = reset_conversation_history(
                question_item["start_time"],
                question_item["send_gametime"][0],
                question_item["from_id"],
                question_item["to_id"],
                list(question.keys())[0],
                state["character_stats"]["characterName"])

    # get impression
    impression_query_data = {
        "from_id": state["userid"],
        "to_id": question_item["from_id"],
        "k": 1
    }
    impression_response = make_api_request_sync("GET", "/impressions/", params=impression_query_data)

    if impression_response["data"]:
        current_impression = impression_response["data"][0]
    else:
        current_impression = []
    logger.info(f"The current impression from User {state['userid']} to User {question_item['from_id']} is {current_impression}")

    # get character_arc
    arc_response = make_api_request_sync("GET", "/character_arc/with_changes", params={"characterId": state["userid"], "k": 1})
    if not arc_response["data"]:
        arc_data = []
    else:
        arc_data = arc_response["data"]
    logger.info(f"User {state['userid']} current character arc is {arc_data}")

    # get featured prompt (reply and impression)
    prompt_response = make_api_request_sync("GET", "/conversation_prompt/", params={"characterId": state["userid"]})
    if not prompt_response:
        others = {}
    else:
        prompt = prompt_response["data"][0]
        relation = prompt["relation"]
        emotion = prompt["emotion"]
        personality = prompt['personality']
        hap = prompt['habits_and_preferences']
        others = {
            "how you treat others": relation,
            "your own emotion": emotion,
            "your own personality": personality,
            "information you want to share": hap
        }
    logger.info(f"User {state['userid']} current conversation prompt is {others}")

    # generate response    
    retry_count = 0
    while retry_count < 3:
        try:
            conversation_response = conversation_responser.invoke(
                {
                    "profile": state["character_stats"],
                    "impression": current_impression,
                    "question": question,
                    "history": history,
                    "impact": state["prompt"]["impression_impact"],
                    "personality": arc_data,
                    "others": others
                }
            )
            break
        except Exception as e:
            logger.error(
                f"⛔ User {state['userid']} Error in generate conversation response: {e}"
            )
            retry_count += 1
            continue

    # check whether this conversation event is finished
    before_finish = question_item["Finish"]
    after_finish = conversation_response["Finish"]
    if after_finish:
        finish_index = before_finish.index(False)
        before_finish[finish_index] = True

    # reconctruct the format
    latest_message = {state["character_stats"]["characterName"]: conversation_response["response"]}
    current_realtime = datetime.now()
    current_day, current_hour, current_minute = calculate_game_time(current_realtime)
    send_gametime = [current_day, f"{current_hour:02}" + ":" + f"{current_minute:02}"]
    send_realtime = f"{current_realtime.year}-{current_realtime.month}-{current_realtime.day} {current_realtime.hour}:{current_realtime.minute:02}"
    response_message = RunningConversation(
        from_id=question_item["to_id"],
        to_id=question_item["from_id"],
        start_time=question_item["start_time"],
        latest_message={state["character_stats"]["characterName"]: conversation_response["response"]},
        send_gametime=send_gametime,
        send_realtime=send_realtime,
        Finish=before_finish
    )
    logger.info(f"A new response message has been generated {response_message}")

    # store the message to database
    store_conversation_data = {
        "from_id": question_item["to_id"],
        "to_id": question_item["from_id"],
        "start_time": question_item["start_time"],
        "start_day": question_item["send_gametime"][0],
        "message": conversation_response["response"],
        "send_gametime": send_gametime,
        "send_realtime": send_realtime,
    }
    store_response = make_api_request_sync("POST", "/conversation/", data=store_conversation_data)
    logger.info(f"User {state['userid']} conversation message stored: {store_response['message']}")

    # send message
    await send_conversation_message(state, response_message)

    return {"response": response_message}


# Check whether all tasks are complete; connect to the starter module for remaining tasks and the end module if all are finished.
def all_conversation_started(state: ConversationState) -> Literal["Conversation_starter", "__end__"]:
    if len(state["daily_task"]) == 0:
        logger.info(f"🧠 ALL CONVERSATIONS HAVE BEEN LAUNCHED.")
        return "__end__"
    else:
        logger.info(f"🧠 NEXT CONVERSATION WILL BE LAUNCHED...")
        return "Conversation_starter"


# check the finish state of conversation message, if not finished, push to waiting_response, otherwise push to handle function
async def check_conversation_state(state: ConversationState, message: RunningConversation):
    if False in message["Finish"]:
        await state["waiting_response"].put(message)
        logger.info(f"🧠 RECEIVE MESSAGE. WAITING FOR RESPONSE...")
    elif message["Finish"] == [True, True]:
        logger.info(f"🧠 SOME CONVERSATIONS ARE FINISHED. UPDATING IMPRESSION...")
        game_time = calculate_game_time(real_time=datetime.now())
        history = reset_conversation_history(
            start_time=message["start_time"],
            start_day=game_time[0],
            id1=message["from_id"],
            id2=message["to_id"],
            name1=list(message["latest_message"].keys())[0],
            name2=state["character_stats"]["characterName"]
        )
        conversation = {
            "characterIds": [message["from_id"], message["to_id"]],
            "dialogue": history,
            "start_time": message["start_time"],
            "start_day": game_time[0]
        }
        await handling_finished_conversation(conversation)


# handling the finished conversations
async def handling_finished_conversation(conversation):  
    logger.info(f"Conversation between Users {conversation['characterIds']} started at {conversation['start_time']} is finished.")

    stored_impression = await update_impression(conversation["characterIds"][0], conversation["characterIds"][1], conversation["dialogue"])
    updated_intimacy = await update_intimacy(conversation["characterIds"][0], conversation["characterIds"][1], conversation["dialogue"])
    return stored_impression, updated_intimacy


async def update_impression(id1: int, id2: int, conversation):
    relation_list = '''
        1.Have a crush,
        2.Secret crush,
        3.Simp,
        4.Partner,
        5.Lover,
        6.Stranger,
        7.Husband and wife / couple,
        8.Ex-wife / ex-husband,
        9.Nemesis,
        10.Benefactor,
        11.Idol,
        12.Mentor and apprentice,
        13.Relative, including Father, Mother, Son, Daughter, Grandfather, Grandmother, Grandson, Granddaughter
    '''

    # update impression
    retry_count = 0
    while retry_count < 3:
        try:
            impression = impression_update.invoke(
                {
                    "conversation": conversation,
                    "relation_list": relation_list
                }
            )
            break
        except Exception as e:
            logger.error(
                f"⛔ User {id1} and User {id2} Error in update impressions: {e}"
            )
            retry_count += 1
            continue

    logger.info(f"🧠 IMPRESSION FROM USER {id1} to USER {id2} UPDATED...")
    logger.info(impression.impression1)
    logger.info(f"🧠 IMPRESSION FROM USER {id2} to USER {id1} UPDATED...")
    logger.info(impression.impression2)

    # Insert impressions to database
    document1 = {
        "from_id": id1,
        "to_id": id2,
        "impression": impression.impression1
    }
    store_impression1_response = make_api_request_sync("POST", "/impressions/", data=document1)
    logger.info(f"From User {id1} to User {id2}: {store_impression1_response['message']}.")

    document2 = {
        "from_id": id2,
        "to_id": id1,
        "impression": impression.impression2
    }
    store_impression2_response = make_api_request_sync("POST", "/impressions/", data=document2)
    logger.info(f"From User {id2} to User {id1}: {store_impression2_response['message']}.")
    return {"new impressions": [impression.impression1, impression.impression2]}


# handle conversations in the read-only list 
async def handling_readonly_conversation(state: ConversationState):
    readonly_conversation = state["ongoing_task"]
    for conversation in readonly_conversation:
        await handling_finished_conversation(conversation)
    state["ongoing_task"] = []


# initialize conversation state when a ws connection is built for certain agent
def initialize_conversation_state(userid, websocket) -> ConversationState:
    # get profile
    character_data = {"characterId": userid}
    profile = make_api_request_sync("GET", "/characters/", params=character_data)
    character_stats = profile["data"][0]
    logger.info(f"User {userid}: {profile['message']}")
    logger.info(f"User {userid} current state is: {character_stats}")

    initial_prompt = {
        "topic_requirements": "",
        "impression_impact": {
            "Relation": "Relation influences the length of conversation and how much information from player profiles should be included.",
            "Emotion": "Emotion determines the tone of the players.",
            "Personlality": "Personality influence the length of each player's answer and their willingness towards conversation.",
            "Habits and preferences": "Habits and preferences are something that one player thinks the other could be interested in and can also be mentioned in the conversation."}
    }
    state = ConversationState(
        userid=userid,
        character_stats=character_stats,
        ongoing_task=[],
        daily_task=[],
        message_queue=asyncio.Queue(),
        waiting_response=asyncio.Queue(),
        websocket=websocket,
        prompt=initial_prompt
    )
    return state


# workflow for planning conversation tasks and starting conversations
def start_conversation_workflow():
    workflow = StateGraph(ConversationState)
    workflow.add_node("Conversation_planner", generate_daily_conversation_plan)
    workflow.add_node("Conversation_starter", start_conversation)
    # workflow.add_node("Task_check", all_conversation_started)
    workflow.set_entry_point("Conversation_planner")
    workflow.add_conditional_edges("Conversation_starter", all_conversation_started)
    workflow.add_edge("Conversation_planner", "Conversation_starter")
    return workflow.compile()


# update intimacy marks
async def update_intimacy(id1: int, id2: int, conversation):
    logger.info(f"🧠 MARKING THE CONVERSATION...")

    character_data = {"characterId": id1}
    profile1 = make_api_request_sync("GET", "/characters/", data=character_data)

    character_data = {"characterId": id2}
    profile2 = make_api_request_sync("GET", "/characters/", data=character_data)

    retry_count = 0
    while retry_count < 3:
        try:
            intimacy_mark = conversation_intimacy_mark.invoke(
                {
                    "profile1": profile1,
                    "profile2": profile2,
                    "conversation": conversation
                }
            )
            break
        except Exception as e:
            logger.error(
                f"⛔ User {id1} and User {id2} Error in updating intimacy score: {e}"
            )
            retry_count += 1
            continue

    logger.info(f"The conversation is {conversation}.")
    logger.info(f"User {id1}'s attitude towards the conversation is: {intimacy_mark.mark1 - 3}")
    logger.info(f"User {id2}'s attitude towards the conversation is: {intimacy_mark.mark2 - 3}")

    intimacy_query_data = {
        "from_id": id1,
        "to_id": id2
    }
    response = make_api_request_sync("GET", "/intimacy/", params=intimacy_query_data)
    if response["data"] is None:
        current_intimacy_1 = 50
        type_1 = "POST"
    else:
        type_1 = "PUT"
        current_intimacy_1 = response["data"][0]["intimacy_level"]

    intimacy_query_data = {
        "from_id": id2,
        "to_id": id1
    }
    response = make_api_request_sync("GET", "/intimacy/", params=intimacy_query_data)
    if response["data"] is None:
        current_intimacy_2 = 50
        type_2 = "POST"
    else:
        type_2 = "PUT"
        current_intimacy_2 = response["data"][0]["intimacy_level"]

    logger.info(f"Past intimacy mark from User {id1} to User {id2} is {current_intimacy_1}.")
    logger.info(f"Past intimacy mark from User {id2} to User {id1} is {current_intimacy_2}.")

    current_intimacy_1 += intimacy_mark.mark1 - 3
    current_intimacy_1 = min(current_intimacy_1, 100)
    current_intimacy_1 = max(current_intimacy_1, 0)
    current_intimacy_2 += intimacy_mark.mark2 - 3
    current_intimacy_2 = min(current_intimacy_2, 100)
    current_intimacy_2 = max(current_intimacy_2, 0)

    logger.info(f"New intimacy mark from User {id1} to User {id2} is {current_intimacy_1}.")
    logger.info(f"New intimacy mark from User {id2} to User {id1} is {current_intimacy_2}.")

    name = "intimacy_level"
    if type_1 == "PUT":
        name = "new_" + name
    update_intimacy_data = {
        "from_id": id1,
        "to_id": id2,
        name: current_intimacy_1
    }
    endpoint = "/intimacy/"
    response = make_api_request_sync(type_1, endpoint, data=update_intimacy_data)
    logger.info(f"From User {id1} to User {id2}: {response['message']}.")

    name = "intimacy_level"
    if type_2 == "PUT":
        name = "new_" + name
    update_intimacy_data = {
        "from_id": id2,
        "to_id": id1,
        name: current_intimacy_2
    }
    endpoint = "/intimacy/"
    response = make_api_request_sync(type_2, endpoint, data=update_intimacy_data)
    logger.info(f"From User {id2} to User {id1}: {response['message']}.")


# a tool for transferring real_time to game_time
def calculate_game_time(real_time=datetime.now(), day1_str='2024-7-1 0:00'):  
    day1 = datetime.strptime(day1_str, "%Y-%m-%d %H:%M")
    elapsed_time = real_time - day1
    game_elapsed_time = elapsed_time * 7
    game_day = game_elapsed_time.days
    total_seconds = int(game_elapsed_time.total_seconds())
    remaining_seconds = total_seconds - (game_day * 86400)  # 86400 秒等于 1 天
    game_hour, remainder = divmod(remaining_seconds, 3600)
    game_minute, seconds = divmod(remainder, 60)
    return [game_day, game_hour, game_minute]


# Query all roles with a message value greater than k and randomly return one role, excluding the user.
def random_user_with_power(k: int, user: int):
    check_response = make_backend_api_request_sync("GET","/characterPower/getAll")
    all_power_list = check_response["data"]
    all_num = len(all_power_list)
    while True:
        index = random.randint(0, all_num-1)
        candidate = all_power_list[index]["characterId"]
        power = all_power_list[index]["currentPower"]
        if power > k and candidate != user:
            final_user = candidate
            break

    return final_user


# randomly generate k conversation times from the current time until 10 minutes before the end of the message value
def generate_talk_time(k: int, id: int):
    day, hour, minute = calculate_game_time(real_time=datetime.now())

    endpoint = "/characterPower/getByCharacterId/" + str(id)
    power_check = make_backend_api_request_sync("GET", endpoint=endpoint)
    if not power_check["data"]:
        return ["000"]
    elif power_check["data"]["currentPower"] < 5:
        return ["000"]
    power_minute = power_check["data"]["currentPower"]

    largest_minute = (24-hour)*60+(0-minute)
    power_minute = min(power_minute, largest_minute//7)
    k = min(k, power_minute//10)    
    time_slot = power_minute//k

    time_list = []
    sorted_numbers = []
    for kk in range(k):
        sorted_numbers.append(random.randint(kk*time_slot+5, (kk+1)*time_slot-5)*7)

    # only for test, set the first conversation to happen after 5 minutes in game time
    sorted_numbers[0] = 5

    for t in sorted_numbers:
        add_hour, add_minute = divmod(minute+t, 60)
        if (hour+add_hour) >= 24:
            break
        elif (hour+add_hour) == 23 and add_minute >= 55:
            break
        start_time = f"{(hour+add_hour):02}" + ":" + f"{add_minute:02}"
        time_list.append(start_time)

    return time_list


# reset the conversation format for storage convenience
def reset_conversation_history(start_time, start_day, id1, id2, name1, name2):
    # get conversation history from database
    get_conversation_params = {
        "from_id": id1,
        "to_id": id2,
        "start_day": start_day,
        "start_time": start_time,
    }
    from_response = make_api_request_sync("GET", "/conversation/", params=get_conversation_params)
    get_conversation_params = {
        "from_id": id2,
        "to_id": id1,
        "start_day": start_day,
        "start_time": start_time,
    }
    to_response = make_api_request_sync("GET", "/conversation/", params=get_conversation_params)
    if not from_response["data"] and not to_response["data"]:
        history = []
    elif not to_response["data"]:
        history = [{name1: t["message"]} for t in from_response["data"]]
    elif not from_response["data"]:
        history = [{name2: t["message"]} for t in to_response["data"]]
    else:
        if len(from_response["data"]) >= len(to_response["data"]):
            first = from_response["data"][::-1]
            first_name = name1
            second = to_response["data"][::-1]
            second_name = name2
        else:
            second = from_response["data"][::-1]
            second_name = name1
            first = to_response["data"][::-1]
            first_name = name2
        history = []
        for i in range(len(second)):
            history.append({first_name: first[i]["message"]})
            history.append({second_name: second[i]["message"]})
        for j in range(len(first[len(second):])):
            history.append({first_name: first[len(second)+j]['message']})
    return history
