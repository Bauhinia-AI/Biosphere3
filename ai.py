import asyncio
import websockets
import json
import os
from datetime import datetime

# 记录连接到AI端的所有托管游戏玩家
connected_clients = set()

# websocket连接->character_id
character_objects = {}

# 记录每个客户端的动作结果
action_results = {}


# 任务1: 事件驱动的任务
async def receive_messages(websocket):
    try:
        async for message in websocket:
            print(f"Received message from game endpoint: {message}")
            response = generate_response(json.loads(message), websocket.remote_address)
            await websocket.send(json.dumps(response))
    except websockets.ConnectionClosed:
        print("Connection closed while receiving messages.")


# 根据消息类型处理消息并生成响应
def generate_response(message, websocket_address):
    message_name = message.get("messageName")
    character_id = message.get("characterId")
    message_code = message.get("messageCode")
    data = message.get("data")
    response = {
        "characterId": character_id,
        "messageCode": message_code,
        "messageName": message_name,
        "data": {},
    }

    # 连接初始化
    if message_name == "connectionInit":
        character_objects[websocket_address] = character_id
        response["data"] = {"result": True, "msg": "character init success"}
    # 动作结果
    elif message_name == "actionresult":
        record_action_result(data, websocket_address)
    # 还有其他的游戏事件待补充
    else:
        response["data"]["msg"] = "Unknown message type."

    return response


# 处理游戏端返回消息的函数
def record_action_result(data, websocket_address):
    character_id = character_objects.get(websocket_address)
    if character_id:
        if character_id not in action_results:
            action_results[character_id] = []
        action_results[character_id].append(data)


# 任务2: 定时发送actionList消息
async def send_scheduled_messages(client):
    while True:
        await asyncio.sleep(5)
        for client in connected_clients:
            character_id = character_objects.get(client.remote_address)
            if character_id is not None:
                message = create_message(
                    character_id,
                    "actionList",
                    6,
                    command=[
                        "goto orchard",
                        "pickapple 20",
                        "goto mine",
                        "gomining 10",
                        "goto fishing",
                        "gofishing 20",
                        "goto home",
                        "sleep 8",
                    ],
                )
                await client.send(json.dumps(message))


# 创建消息的辅助函数
def create_message(character_id, message_name, message_code, **kwargs):
    return {
        "characterId": character_id,
        "messageCode": message_code,
        "messageName": message_name,
        "data": kwargs,
    }


# 处理游戏端连接
async def handler(websocket, path):
    connected_clients.add(websocket)
    print(
        f"Client connected from {websocket.remote_address}. Total connected clients: {len(connected_clients)}"
    )
    try:
        # 并发任务1: 接收消息
        receive_task = asyncio.create_task(receive_messages(websocket))
        # 并发任务2: 定时发送消息
        send_task = asyncio.create_task(send_scheduled_messages(websocket))
        await asyncio.gather(receive_task, send_task)
    except websockets.ConnectionClosed:
        print(f"Connection closed from {websocket.remote_address}")
    finally:
        persist_data(websocket.remote_address)
        character_id = character_objects[websocket.remote_address]
        del character_objects[websocket.remote_address]
        print(f"Character object for ID {character_id} removed.")

        connected_clients.remove(websocket)
        print(
            f"Client disconnected from {websocket.remote_address}. Total connected clients: {len(connected_clients)}"
        )


# 在连接断开时持久化数据
def persist_data(websocket_address):
    character_id = character_objects.get(websocket_address)
    if character_id and character_id in action_results:
        # 确保目录存在
        directory = "action_results"
        if not os.path.exists(directory):
            os.makedirs(directory)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{directory}/{character_id}_{timestamp}.json"
        with open(filename, "w") as f:
            json.dump(action_results[character_id], f, indent=4)
        print(f"Data for {character_id} saved to {filename}")
        # 清除已保存的数据
        del action_results[character_id]


async def main():
    host = "localhost"
    port = 6789
    server = await websockets.serve(handler, host, port)
    print(f"WebSocket server started at ws://{host}:{port}")
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
