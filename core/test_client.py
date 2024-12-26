import asyncio
import websockets
import json
from conversation_srv.conversation_model import RunningConversation
from datetime import datetime
from conversation_srv.conversation_engine import *

current_realtime = datetime.now()
current_day, current_hour, current_minute = calculate_game_time(current_realtime)
send_gametime = [current_day, f"{current_hour:02}" + ":" + f"{current_minute:02}"]
send_realtime = f"{current_realtime.year}-{current_realtime.month}-{current_realtime.day} {current_realtime.hour}:{current_realtime.minute:02}"
messages = [
        RunningConversation(
            from_id=2,
            to_id=1,
            start_time="11:00",
            latest_message={"Bob": "Hello Alice! Do you have any math classes today?"},
            send_realtime=send_realtime,
            send_gametime=send_gametime,
            Finish=[False, False]
        ),
        RunningConversation(
            from_id=2,
            to_id=1,
            start_time="11:00",
            latest_message={"Bob": "Although final exams are very important, you still need to have enough sleep."},
            send_realtime=send_realtime,
            send_gametime=send_gametime,
            Finish=[True, False]
        ),
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
        RunningConversation(
            from_id=2,
            to_id=1,
            start_time="11:00",
            latest_message={"Bob": "That's ridiculous."},
            send_realtime=send_realtime,
            send_gametime=send_gametime,
            Finish=[True, True])
        ]


async def test_client():
    uri = "ws://localhost:6789"
    async with websockets.connect(uri) as websocket:
        character_id = 1

        # send_message to initial a character
        init_message = {
            "characterId": character_id,
            "messageName": "connectionInit",
            "data": {},
        }
        await websocket.send(json.dumps(init_message))
        response = await websocket.recv()
        print(f"Received response: {response}")


        for msg in messages:
            await asyncio.sleep(1)  
            await websocket.send(json.dumps(create_message(character_id, "to_agent", msg)))
            print(f"Sent message: {json.dumps(create_message(character_id, 'to_agent', msg))}")
            await asyncio.sleep(20)

            # await websocket.send(json.dumps(create_message(character_id, "read_only", msg)))
            # print(f"Sent message: {json.dumps(create_message(character_id, 'read_only', msg))}")
        await websocket.close()


asyncio.run(test_client())
