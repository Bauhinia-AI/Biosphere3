# test_client.py

import asyncio
import websockets
import json


async def test_client():
    uri = "ws://localhost:6789"
    async with websockets.connect(uri) as websocket:
        character_id = "test_character"

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
        messages = [
            # one step
            {"messageName": "onestep"},
            # action result
            # {"messageName": "action_result", "data": {"result": "success"}},
            # {"messageName": "check"},
        ]

        for msg in messages:
            await asyncio.sleep(1)  # 模拟消息间的延迟
            await websocket.send(json.dumps(msg))
            print(f"Sent message: {msg}")

        # 关闭连接
        await websocket.close()


asyncio.run(test_client())
