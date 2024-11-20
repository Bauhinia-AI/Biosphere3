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
from core.db.database_api_utils import make_api_request_async, make_api_request_sync
from datetime import datetime, timedelta
import random

os.environ["OPENAI_API_KEY"] = "sk-VTpN30Day8RP7IDVVRVWx4vquVhGViKftikJw82WIr94DaiC"

conversation_topic_planner = conversation_topic_planner_prompt | ChatOpenAI(
    base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini", temperature=1.0
).with_structured_output(ConversationTopics)

conversation_planner = conversation_planner_prompt | ChatOpenAI(
    base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini", temperature=1.0
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
    base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini", temperature=1.0
).with_structured_output(IntimacyMark)


async def generate_daily_conversation_plan(state: ConversationState):
    neighbour_list = []  # 取出neighbour_list，从数据库
    # 处理前一天剩余的readonly对话
    if len(state["ongoing_task"]) != 0:
        await handling_readonly_conversation(state)
    # 重置状态中的任务队列
    # state["finished_task"] = []
    state["daily_task"] = []

    # 更新当前用户的profile，从数据库获取
    userid = state["userid"]
    character_data = {"characterId": userid}
    profile = make_api_request_sync("POST", "/characters/get", data=character_data)
    state["character_stats"] = profile["data"][0]
    logger.info(f"User {state['userid']}: {profile['message']}")
    logger.info(f"User {state['userid']} current state is: {state['character_stats']}")

    # To do
    # 获取其他记忆
    get_daily_objectives_data = {"characterId": state["userid"], "k": 1}
    objective_response = make_api_request_sync(
        "POST", "/daily_objectives/get", data=get_daily_objectives_data
    )
    if objective_response["data"] is not None:
        memory = objective_response["data"]
    else:
        memory = []
    # 生成对话主题列表
    topic_list = conversation_topic_planner.invoke(
        {
            "character_stats": state["character_stats"],
            "memory": memory,
            "requirements": state["prompt"]["topic_requirements"],
        }
    )
    logger.info(
        f"Today User {state['userid']} is going to talk with others about: {topic_list['topics']}"
    )

    # rag对话对象candidate
    final_topic_list = []  # 每个条目包含topic，对话对象，impression三个字段
    for topic in topic_list["topics"]:
        # To do
        # 在给定范围的列表中进行rag
        # neighbour_list加入
        encounter_data = {"from_id": 1, "k": 3}
        encounter_response = make_api_request_sync(
            "POST", "/encounter_count/get_by_from_id", data=encounter_data
        )
        if encounter_response["data"] is None:
            character_rag_data = {
                "characterId": state["userid"],
                "topic": topic,
                "k": 2,
            }
            rag_response = make_api_request_sync(
                "POST", "/characters/get_rag", data=character_rag_data
            )
        else:
            candidate_list = []
            for item in encounter_response["data"]:
                candidate_list.append(item["to_id"])
            character_rag_data = {
                "characterId": state["userid"],
                "characterList": candidate_list,
                "topic": topic,
                "k": 2,
            }
            rag_response = make_api_request_sync(
                "POST", "/characters/get_rag_in_list", data=character_rag_data
            )

        # 模拟rag结果
        # rag_response = {"data": [{"characterId": 2}, {"characterId": 1}]}

        if len(rag_response["data"]) == 0:
            logger.info(
                f"User {state['userid']}: There is no suitable person to talk to on this topic {topic}."
            )

        for user in rag_response["data"]:
            if user["characterId"] != state["userid"]:  # 排除自己和自己对话
                impression_query_data = {
                    "from_id": state["userid"],
                    "to_id": user["characterId"],
                    "k": 1,
                }
                impression_response = make_api_request_sync(
                    "POST", "/impressions/get", data=impression_query_data
                )

                # impression为空报错机制
                if impression_response["data"]:
                    current_impression = impression_response["data"][0]
                else:
                    current_impression = []
                current_topic_list = {
                    "topic": topic,
                    "userid": user["characterId"],
                    "impression": current_impression,
                }
                final_topic_list.append(current_topic_list)
                break

    conversation_plan = DailyConversationPlan(conversations=[])
    timetable = 10  # 对话开始时间的
    for talk in final_topic_list:
        pre_single_conversation = conversation_planner.invoke(
            {
                "character_stats": state["character_stats"],
                "topic_list": talk,
            }
        )
        start_minute = (state["userid"] % 60 + random.randint(0, 60)) % 60
        start_time = str(timetable) + ":" + f"{start_minute:02}"
        timetable += 1
        # 重组格式
        single_conversation = ConversationTask(
            from_id=state["userid"],
            to_id=talk["userid"],
            start_time=start_time,
            topic=talk["topic"],
            dialogue=[
                {
                    state["character_stats"]["characterName"]: pre_single_conversation[
                        "first_sentence"
                    ]
                }
            ],
            Finish=[False, False],
        )
        conversation_plan.conversations.append(single_conversation)

    # 更新每日计划到state
    state["daily_task"] = conversation_plan.conversations

    logger.info(f"🧠 DAILY CONVERSATION PLAN GENERATED...")
    logger.info(
        f"Daily conversation plan of User {state['userid']}: {state['daily_task']}"
    )
    return state


def create_message(
    character_id, message_name, conversation: RunningConversation, message_code=100
):  # 对话系统messagecode100
    return {
        "characterId": character_id,
        "messageCode": message_code,
        "messageName": message_name,
        "data": conversation,
    }


# 发送消息
async def send_conversation_message(
    state: ConversationState, conversation: RunningConversation
):
    websocket = state["websocket"]
    if websocket is None or websocket.closed:
        logger.error(f"⛔ User {state['userid']}: WebSocket is not connected.")
        return
    try:
        message = create_message(
            character_id=state["userid"],
            message_name="to_agent",
            conversation=conversation,
        )
        await websocket.send(json.dumps(message))
        logger.info(f"📤 User {state['userid']}: Sent a response message: {message}")
    except websockets.ConnectionClosed:
        logger.warning(
            f"User {state['userid']}: WebSocket connection closed during send."
        )
    except Exception as e:
        logger.error(f"User {state['userid']}: Error sending message: {e}")


async def start_conversation(state: ConversationState):
    current_talk = state["daily_task"][0]  # 当前对话任务，等待检查
    logger.info(f"User {state['userid']}: current conversation task is {current_talk}.")
    game_start_time = current_talk["start_time"]
    # 解析时间字符串
    time_obj = datetime.strptime(game_start_time, "%H:%M")
    # 获取小时和分钟
    start_hour = time_obj.hour
    start_minute = time_obj.minute
    current_time = calculate_game_time(datetime.now())
    if current_time[1] < start_hour or (
        current_time[1] == start_hour and current_time[2] < start_minute
    ):
        # 计算下一次开始对话时间
        sleep_time = (
            (-current_time[1] + start_hour) * 60 * 60
            + (-current_time[2] + start_minute) * 60
        ) // 7
        logger.info(
            f"User {state['userid']}: next conversation will be started after {sleep_time} seconds."
        )
        await asyncio.sleep(
            sleep_time - 5
        )  # 设定定时任务，考虑执行check步骤需要的时间-5秒
    else:
        logger.info(
            f"User {state['userid']} missed one conversation. Start this task right now..."
        )
        current_talk["start_time"] = str(current_time[1]) + ":" + str(current_time[2])

    # 从数据库获取当前用户的最新状态
    userid = state["userid"]
    character_data = {"characterId": userid}
    profile = make_api_request_sync("POST", "/characters/get", data=character_data)
    state["character_stats"] = profile["data"][0]
    logger.info(f"User {state['userid']}: {profile['message']}")
    logger.info(f"User {state['userid']} current state is: {state['character_stats']}")

    # 获取当天已经发生的对话列表
    talked_data = {"characterId": state["userid"], "day": current_time[0]}
    talked_response = make_api_request_sync(
        "POST", "/conversations/get_by_id_and_day", data=talked_data
    )
    talked = talked_response["data"]

    logger.info(f"🧠 CHECKING WHETHER TO START THE CONVERSATION ...")
    check_response = conversation_check.invoke(
        {
            "profile": state["character_stats"],
            "current_talk": current_talk,
            "finished_talk": talked,
        }
    )  # 检验对话任务是否有必要

    if check_response["Need"]:
        talk_message = RunningConversation(
            from_id=current_talk["from_id"],
            to_id=current_talk["to_id"],
            start_time=current_talk["start_time"],
            latest_message=current_talk["dialogue"][0],
            dialogue=current_talk["dialogue"],
            Finish=[False, False],
        )

        # 发送消息
        await send_conversation_message(state, talk_message)

        logger.info(
            f"The conversation FROM {current_talk['from_id']} TO {current_talk['to_id']} at GAME TIME {current_talk['start_time']} has started."
        )
    else:
        logger.info(
            f"The conversation FROM {current_talk['from_id']} TO {current_talk['to_id']} at GAME TIME {current_talk['start_time']} is canceled after check."
        )

    # 更新daily_task队列
    if len(state["daily_task"]) > 1:
        state["daily_task"] = state["daily_task"][1:]
    else:
        state["daily_task"] = []

    return state


# 收到消息生成回复
async def generate_response(state: ConversationState):
    question_item = await state["waiting_response"].get()
    dialogue = question_item.copy()

    if question_item is None:
        logger.error(f"User {state['userid']}: No conversation is waiting for reply.")
    logger.info(f"User {state['userid']}: is replying the message: {question_item}")
    logger.info(f"🧠 GENERATING RESPONSE...")

    # 更新当前用户的profile，从数据库获取
    userid = state["userid"]
    character_data = {"characterId": userid}
    profile = make_api_request_sync("POST", "/characters/get", data=character_data)
    state["character_stats"] = profile["data"][0]
    logger.info(f"User {state['userid']}: {profile['message']}")
    logger.info(f"User {state['userid']} current state is: {state['character_stats']}")

    question = question_item["latest_message"]
    history = question_item["dialogue"]

    # 获得印象，从数据库
    impression_query_data = {
        "from_id": state["userid"],
        "to_id": question_item["from_id"],
        "k": 1,
    }
    impression_response = make_api_request_sync(
        "POST", "/impressions/get", data=impression_query_data
    )
    logger.info(
        f"The current impression from User {state['userid']} to User {question_item['from_id']} is {impression_response['data'][0]}"
    )

    conversation_response = conversation_responser.invoke(
        {
            "profile": state["character_stats"],
            "impression": impression_response["data"][0],
            "question": question,
            "history": history,
            "impact": state["prompt"]["impression_impact"],
        }
    )
    # conversation_response = {"response": "", "Finish": [False, False]}
    # 判断通话是否结束
    before_finish = question_item["Finish"]
    after_finish = conversation_response["Finish"]
    if after_finish:
        finish_index = before_finish.index(False)
        before_finish[finish_index] = True

    # 重组格式
    latest_message = {
        state["character_stats"]["characterName"]: conversation_response["response"]
    }
    dialogue["dialogue"].append(latest_message)
    response_message = RunningConversation(
        from_id=question_item["to_id"],
        to_id=question_item["from_id"],
        start_time=question_item["start_time"],
        latest_message={
            state["character_stats"]["characterName"]: conversation_response["response"]
        },
        dialogue=dialogue["dialogue"],
        Finish=before_finish,
    )
    logger.info(f"A new response message has been generated {response_message}")

    # 发送消息
    await send_conversation_message(state, response_message)

    return {"response": response_message["latest_message"]}


# 判断是否所有任务都已经完成，如果有未开始的对话，连接到starter模块，如果所有对话都已发出，连接到end，发起对话流程结束
def all_conversation_started(
    state: ConversationState,
) -> Literal["Conversation_starter", "__end__"]:
    if len(state["daily_task"]) == 0:
        logger.info(f"🧠 ALL CONVERSATIONS HAVE BEEN LAUNCHED.")
        return "__end__"
    else:
        logger.info(f"🧠 NEXT CONVERSATION WILL BE LAUNCHED...")
        return "Conversation_starter"


# 判断收到的消息对话状态，如果需要回复(Finish中存在True)则排队到waiting response，如果已经结束(False),则转到handle函数
async def check_conversation_state(
    state: ConversationState, message: RunningConversation
):
    if False in message["Finish"]:
        await state["waiting_response"].put(message)
        logger.info(f"🧠 RECEIVE MESSAGE. WAITING FOR RESPONSE...")
    elif message["Finish"] == [True, True]:
        logger.info(f"🧠 SOME CONVERSATIONS ARE FINISHED. UPDATING IMPRESSION...")
        game_time = calculate_game_time()
        conversation = {
            "characterIds": [message["from_id"], message["to_id"]],
            "dialogue": message["dialogue"],
            "start_time": message["start_time"],
            "start_day": game_time[0],
        }
        await handling_finished_conversation(conversation)


# 处理已经结束的对话，包括生成印象，储存到数据库
async def handling_finished_conversation(
    conversation,
):  # conversation = character_ids[], dialogue, start_time
    # 储存对话到数据库
    stored_conversation_response = make_api_request_sync(
        "POST", "/conversations/store", data=conversation
    )
    logger.info(
        f"Conversation between Users {conversation['characterIds']} started at {conversation['start_time']} is finished."
    )
    logger.info(conversation["dialogue"])
    logger.info(stored_conversation_response["message"])

    stored_impression = await update_impression(
        conversation["characterIds"][0],
        conversation["characterIds"][1],
        conversation["dialogue"],
    )
    updated_intimacy = await update_intimacy(
        conversation["characterIds"][0],
        conversation["characterIds"][1],
        conversation["dialogue"],
    )
    return stored_impression, updated_intimacy


async def update_impression(id1: int, id2: int, conversation):
    relation_list = """
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
    """

    impression = impression_update.invoke(
        {"conversation": conversation, "relation_list": relation_list}
    )

    # logger
    logger.info(f"🧠 IMPRESSION FROM USER {id1} to USER {id2} UPDATED...")
    logger.info(impression.impression1)
    logger.info(f"🧠 IMPRESSION FROM USER {id2} to USER {id1} UPDATED...")
    logger.info(impression.impression2)

    # Insert impressions:
    document1 = {"from_id": id1, "to_id": id2, "impression": impression.impression1}
    store_impression1_response = make_api_request_sync(
        "POST", "/impressions/store", data=document1
    )
    logger.info(
        f"From User {id1} to User {id2}: {store_impression1_response['message']}."
    )

    document2 = {"from_id": id2, "to_id": id1, "impression": impression.impression2}
    store_impression2_response = make_api_request_sync(
        "POST", "/impressions/store", data=document2
    )
    logger.info(
        f"From User {id2} to User {id1}: {store_impression2_response['message']}."
    )
    return {"new impressions": [impression.impression1, impression.impression2]}


async def generate_knowledge(state: ConversationState):
    profile = state["character_stats"]

    # 获得当天所有通话的记录
    current_time = calculate_game_time()
    talked_data = {"characterId": state["userid"], "day": current_time[0]}
    talked_response = make_api_request_sync(
        "POST", "/conversations/get_by_id_and_day", data=talked_data
    )
    conversation_list = talked_response["data"]
    # conversation_list = []

    logger.info(f"🧠 REFLECTING ON TODAY'S CONVERSATIONS...")

    knowledge = knowledge_generator.invoke(
        {"player": profile, "conversation_list": conversation_list}
    )

    # logger
    logger.info(f"{state['userid']} have learned something from the environment.")
    logger.info(knowledge.environment_information)
    logger.info(f"{state['userid']} have learned something about himself/herself.")
    logger.info(knowledge.personal_information)

    return {
        "environment knowledge": knowledge.environment_information,
        "personal knowledge": knowledge.personal_information,
    }


# 用于定时处理只读列表中的所有通话，每个一段时间认为通话已经结束，进入结束对话流程
async def handling_readonly_conversation(state: ConversationState):
    readonly_conversation = state["ongoing_task"]
    for conversation in readonly_conversation:
        await handling_finished_conversation(conversation)
    state["ongoing_task"] = []


# 初始化实例
def initialize_conversation_state(userid, websocket) -> ConversationState:
    # 获取用户的profile，从数据库获取
    character_data = {"characterId": userid}
    profile = make_api_request_sync("POST", "/characters/get", data=character_data)
    character_stats = profile["data"][0]
    logger.info(f"User {userid}: {profile['message']}")
    logger.info(f"User {userid} current state is: {character_stats}")

    initial_prompt = {
        "topic_requirements": "",
        "impression_impact": {
            "Relation": "Relation influences the length of conversation and how much information from player profiles should be included.",
            "Emotion": "Emotion determines the tone of the players.",
            "Personlality": "Personality influence the length of each player's answer and their willingness towards conversation.",
            "Habits and preferences": "Habits and preferences are something that one player thinks the other could be interested in and can also be mentioned in the conversation.",
        },
    }
    state = ConversationState(
        userid=userid,
        character_stats=character_stats,
        ongoing_task=[],
        daily_task=[],
        message_queue=asyncio.Queue(),
        waiting_response=asyncio.Queue(),
        websocket=websocket,
        prompt=initial_prompt,
    )
    return state


# 每日规划，主动发起对话的流程
def start_conversation_workflow():
    workflow = StateGraph(ConversationState)
    workflow.add_node("Conversation_planner", generate_daily_conversation_plan)
    workflow.add_node("Conversation_starter", start_conversation)
    # workflow.add_node("Task_check", all_conversation_started)
    workflow.set_entry_point("Conversation_planner")
    workflow.add_conditional_edges("Conversation_starter", all_conversation_started)
    workflow.add_edge("Conversation_planner", "Conversation_starter")
    return workflow.compile()


# 更新亲密度
async def update_intimacy(id1: int, id2: int, conversation):
    logger.info(f"🧠 MARKING THE CONVERSATION...")

    character_data = {"characterId": id1}
    profile1 = make_api_request_sync("POST", "/characters/get", data=character_data)

    character_data = {"characterId": id2}
    profile2 = make_api_request_sync("POST", "/characters/get", data=character_data)

    intimacy_mark = conversation_intimacy_mark.invoke(
        {"profile1": profile1, "profile2": profile2, "conversation": conversation}
    )

    logger.info(f"The conversation is {conversation}.")
    logger.info(
        f"User {id1}'s attitude towards the conversation is: {intimacy_mark.mark1 - 3}"
    )
    logger.info(
        f"User {id2}'s attitude towards the conversation is: {intimacy_mark.mark2 - 3}"
    )

    # 获取旧亲密度，如果不存在表示第一次对话，默认值50
    intimacy_query_data = {"from_id": id1, "to_id": id2}

    response = make_api_request_sync("POST", "/intimacy/get", data=intimacy_query_data)
    if response["data"] is None:
        current_intimacy_1 = 50
        type_1 = "store"
    else:
        type_1 = "update"
        current_intimacy_1 = response["data"][0]["intimacy_level"]

    intimacy_query_data = {"from_id": id2, "to_id": id1}

    response = make_api_request_sync("POST", "/intimacy/get", data=intimacy_query_data)
    if response["data"] is None:
        current_intimacy_2 = 50
        type_2 = "store"
    else:
        type_2 = "update"
        current_intimacy_2 = response["data"][0]["intimacy_level"]

    logger.info(
        f"Past intimacy mark from User {id1} to User {id2} is {current_intimacy_1}."
    )
    logger.info(
        f"Past intimacy mark from User {id2} to User {id1} is {current_intimacy_2}."
    )

    # 返回1-5，修改为-2到+2，同时截断
    current_intimacy_1 += intimacy_mark.mark1 - 3
    current_intimacy_1 = min(current_intimacy_1, 100)
    current_intimacy_1 = max(current_intimacy_1, 0)
    current_intimacy_2 += intimacy_mark.mark2 - 3
    current_intimacy_2 = min(current_intimacy_2, 100)
    current_intimacy_2 = max(current_intimacy_2, 0)

    logger.info(
        f"New intimacy mark from User {id1} to User {id2} is {current_intimacy_1}."
    )
    logger.info(
        f"New intimacy mark from User {id2} to User {id1} is {current_intimacy_2}."
    )

    # 更新亲密度，区分新增和更新数据库命令的不同
    name = "intimacy_level"
    if type_1 == "update":
        name = "new_" + name
    update_intimacy_data = {"from_id": id1, "to_id": id2, name: current_intimacy_1}
    endpoint = "/intimacy/" + type_1
    response = make_api_request_sync("POST", endpoint, data=update_intimacy_data)
    logger.info(f"From User {id1} to User {id2}: {response['message']}.")

    name = "intimacy_level"
    if type_2 == "update":
        name = "new_" + name
    update_intimacy_data = {"from_id": id2, "to_id": id1, name: current_intimacy_2}
    endpoint = "/intimacy/" + type_2
    response = make_api_request_sync("POST", endpoint, data=update_intimacy_data)
    logger.info(f"From User {id2} to User {id1}: {response['message']}.")


# 现实时间到游戏时间转换器
def calculate_game_time(
    real_time=datetime.now(), day1_str="2024-11-11 20:00"
):  # 暂时设置的day1，real_time=datetime.now()
    # 解析现实时间
    day1 = datetime.strptime(day1_str, "%Y-%m-%d %H:%M")
    # 第1天的开始时间
    # 计算经过的时间
    elapsed_time = real_time - day1
    # 游戏时间流速为现实的7倍
    game_elapsed_time = elapsed_time * 7
    # 计算游戏时间
    game_day = game_elapsed_time.days
    total_seconds = int(game_elapsed_time.total_seconds())
    remaining_seconds = total_seconds - (game_day * 86400)  # 86400 秒等于 1 天
    # 计算小时、分钟和秒
    game_hour, remainder = divmod(remaining_seconds, 3600)
    game_minute, seconds = divmod(remainder, 60)
    return [game_day, game_hour, game_minute]
