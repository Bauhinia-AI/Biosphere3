# test_client.py

import asyncio
import websockets
import json
from conversation_srv.conversation_model import RunningConversation
from datetime import datetime


def calculate_game_time(real_time=datetime.now(), day1_str='2024-7-1 0:00'):  # 暂时设置的day1，real_time=datetime.now()
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

def create_message(character_id, message_name, conversation, message_code=100):
    return {
        "characterId": character_id,
        "messageCode": message_code,
        "messageName": message_name,
        "data": conversation,
    }

current_realtime = datetime.now()
current_day, current_hour, current_minute = calculate_game_time(current_realtime)
send_gametime = [current_day, f"{current_hour:02}" + ":" + f"{current_minute:02}"]
send_realtime = f"{current_realtime.year}-{current_realtime.month}-{current_realtime.day} {current_realtime.hour}:{current_realtime.minute:02}"
messages = [
        # RunningConversation(
        #     from_id=2,
        #     to_id=1,
        #     start_time="11:00",
        #     latest_message={"Bob": "Hello Alice! Do you have any math classes today?"},
        #     send_realtime=send_realtime,
        #     send_gametime=send_gametime,
        #     Finish=[False, False]
        # ),
        # RunningConversation(
        #     from_id=2,
        #     to_id=1,
        #     start_time="11:00",
        #     latest_message={"Bob": "Although final exams are very important, you still need to have enough sleep."},
        #     send_realtime=send_realtime,
        #     send_gametime=send_gametime,
        #     Finish=[True, False]
        # ),
        RunningConversation(
            from_id=2,
            to_id=1,
            start_time="13:00",
            latest_message={"Bob": "No. I'm trying to understand you but your way of life is totally wrong."},
            send_realtime=send_realtime,
            send_gametime=send_gametime,
            Finish=[True, False]
        ),
        RunningConversation(
            from_id=2,
            to_id=1,
            start_time="13:00",
            latest_message={"Bob": "You don't need to worry about that. I'm good at math. I can help you prepare for the exams."},
            send_realtime=send_realtime,
            send_gametime=send_gametime,
            Finish=[True, False]
        ),
        # RunningConversation(
        #     from_id=2,
        #     to_id=1,
        #     start_time="11:00",
        #     latest_message={"Bob": "That's ridiculous."},
        #     send_realtime=send_realtime,
        #     send_gametime=send_gametime,
        #     Finish=[True, True])
        ]


async def test_client():
    uri = "ws://localhost:6789"
    async with websockets.connect(uri) as websocket:
        character_id = 1

        # 发送初始化消息
        init_message = {
            "characterId": character_id,
            "messageName": "connectionInit",
            "data": {},
        }
        await websocket.send(json.dumps(init_message))
        response = await websocket.recv()
        print(f"Received response: {response}")

        # 发送一系列消息
        # messages = [
        #     # one step
        #     {"messageName": "onestep"},
        #     # action result
        #     # {"messageName": "action_result", "data": {"result": "success"}},
        #     # {"messageName": "check"},
        # ]

        for msg in messages:
            await asyncio.sleep(1)  # 模拟消息间的延迟
            await websocket.send(json.dumps(create_message(character_id, "to_agent", msg)))
            print(f"Sent message: {json.dumps(create_message(character_id, 'to_agent', msg))}")
            await asyncio.sleep(20)

            # await websocket.send(json.dumps(create_message(character_id, "read_only", msg)))
            # print(f"Sent message: {json.dumps(create_message(character_id, 'read_only', msg))}")

        # await asyncio.sleep(100)


        # 关闭连接
        await websocket.close()


asyncio.run(test_client())
