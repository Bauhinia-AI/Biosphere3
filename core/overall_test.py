import asyncio
import websockets
from conversation_instance import ConversationInstance
from conversation_srv.conversation_model import *
from conversation_srv.conversation_engines import *
from conversation_srv.conversation_prompts import *


def create_message(character_id, message_name, conversation, message_code=00000):
    return {
        "characterId": character_id,
        "messageCode": message_code,
        "messageName": message_name,
        "data": conversation,
    }


async def main():
    agent_1 = ConversationInstance(user_id=1)  # Alice
    # agent_2 = ConversationInstance(user_id=2)  # Bob

    messages = [
        RunningConversation(
            from_id=2,
            to_id=1,
            start_time="",
            latest_message={"Bob": "Hello Alice! Do you have any math classes today?"},
            dialogue=[],
            Finish=[False, False]
        ),
        RunningConversation(
            from_id=2,
            to_id=1,
            start_time="",
            latest_message={"Bob": "That's great! See you tomorrow."},
            dialogue=[
                {"Bob": "Hello Alice! Why do you look so tired?"},
                {"Alice": "Hello Bob! I'm preparing for the final exams. I've been staying up late for days."},
                {"Bob": "Although final exams are very important, you still need to have enough sleep."},
                {"Alice": "But math courses are too difficult. I'm really worried whether I could pass the exams."},
                {"Bob": "You don't need to worry about that. I'm good at math. I can help you prepare for the exams."},
                {"Alice": "That's great! Are you free tomorrow evening? We can meet at the library to study together."},
                {"Bob": "Sorry, I have an important business meeting tomorrow afternoon. What about tomorrow evening?"},
                {"Alice": "Sure, I'm free all day. I can wait for you in the library."},
                {"Bob": "That's great! See you tomorrow."}
            ],
            Finish=[True, False]
        ),
        RunningConversation(
            from_id=2,
            to_id=1,
            start_time="10:00:00",
            latest_message={"Bob": "That's great! See you tomorrow."},
            dialogue=[
                {"Bob": "Hello Alice! Why do you look so tired?"},
                {"Alice": "Hello Bob! I'm preparing for the final exams. I've been staying up late for days."},
                {"Bob": "Although final exams are very important, you still need to have enough sleep."},
                {"Alice": "But math courses are too difficult. I'm really worried whether I could pass the exams."},
            ],
            Finish=[True, False]
        ),
        RunningConversation(
            from_id=2,
            to_id=1,
            start_time="10:00:00",
            latest_message={"Bob": "That's great! See you tomorrow."},
            dialogue=[
                {"Bob": "Hello Alice! Why do you look so tired?"},
                {"Alice": "Hello Bob! I'm preparing for the final exams. I've been staying up late for days."},
                {"Bob": "Although final exams are very important, you still need to have enough sleep."},
                {"Alice": "But math courses are too difficult. I'm really worried whether I could pass the exams."},
                {"Bob": "You don't need to worry about that. I'm good at math. I can help you prepare for the exams."},
                {"Alice": "That's great! Are you free tomorrow evening? We can meet at the library to study together."},
                {"Bob": "Sorry, I have an important business meeting tomorrow afternoon. What about tomorrow evening?"},
                {"Alice": "Sure, I'm free all day. I can wait for you in the library."},
                {"Bob": "That's great! See you tomorrow."}
            ],
            Finish=[True, False]
        ),
        RunningConversation(
            from_id=2,
            to_id=1,
            start_time="11:00:00",
            latest_message={"Bob": "That's ridiculous."},
            dialogue=[
                {"Bob": "Hello Alice! Why do you look so tired?"},
                {"Alice": "Hello Bob! I'm preparing for the final exams. I've been staying up late for days."},
                {"Bob": "Although final exams are very important, you still need to have enough sleep."},
                {"Alice": "I can't agree with you. Final exams are more important than anything."},
                {"Bob": "But health is also very important. If you still learn in this way, you will get sick."},
                {"Alice": "That's none of your business. I have my own learning habit. You can not understand me at all"},
                {"Bob": "No. I'm trying to understand you but your way of life is totally wrong."},
                {"Alice": "Shut up! I don't want to talk with you any more. Get out!"},
                {"Bob": "That's ridiculous."}
            ],
            Finish=[True, True])
        ]

    # 开始测试
    # 发起对话
    # message = create_message(1, "neighbour_list", [])
    # await agent_1.listener(json.dumps(message))
    # await asyncio.sleep(5)  # 等待创建任务
    # await agent_1.plan_start_task

    # 回复和只读交替
    await asyncio.sleep(5)
    message = create_message(1, "to_agent", messages[0])  # 回复
    await agent_1.listener(json.dumps(message))
    message = create_message(1, "read_only", messages[2])  # 只读
    await agent_1.listener(json.dumps(message))
    await asyncio.sleep(3)
    message = create_message(1, "read_only", messages[3])  # 同一个对话时间的只读
    await agent_1.listener(json.dumps(message))
    # message = create_message(1, "to_agent", messages[1])  # 回复，完成后注意状态改变
    # await agent_1.listener(json.dumps(message))
    message = create_message(1, "to_agent", messages[4])  # 已经结束的对话
    await agent_1.listener(json.dumps(message))

    await asyncio.sleep(120)  # 防止主线程终止导致规划任务没有全部完成就退出
if __name__ == "__main__":
    asyncio.run(main())
