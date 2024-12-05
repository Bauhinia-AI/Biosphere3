import asyncio
import websockets
import json


async def test_client():
    uri = "ws://localhost:6789"  # 与 ai.py 中的 WebSocket 服务器地址和端口匹配
    async with websockets.connect(uri) as websocket:
        # 发送初始化消息以获取 character_id
        init_message = {
            "characterId": 43,  # 示例 characterId
            "messageCode": 1,
            "messageName": "connectionInit",
            "data": {"msg": "client request character init"},
        }
        await websocket.send(json.dumps(init_message))
        print(f"Sent init message: {init_message}")

        # 接收服务器的响应
        response = await websocket.recv()
        print(f"Received response: {response}")
        # 等待下条消息
        response = await websocket.recv()
        print(f"Received response: {response}")


async def main():
    await test_client()


if __name__ == "__main__":
    asyncio.run(main())
