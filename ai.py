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


# 处理游戏端发送的消息
async def receive_messages(websocket):
    try:
        async for message in websocket:
            print(f"Received message from game endpoint: {message}")
            response = generate_response(json.loads(message), websocket.remote_address)
            await websocket.send(json.dumps(response))
    except websockets.ConnectionClosed:
        print("Connection closed while receiving messages.")


# 处理游戏端返回消息的函数
def record_action_result(data, websocket_address):
    character_id = character_objects.get(websocket_address)
    if character_id:
        if character_id not in action_results:
            action_results[character_id] = []
        action_results[character_id].append(data)


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


# 根据消息类型生成响应
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

    if message_name == "connectionInit":
        character_objects[websocket_address] = character_id
        response["data"] = {"result": True, "msg": "character init success"}
    elif message_name == "actionresult":
        record_action_result(data, websocket_address)
    else:
        response["data"]["msg"] = "Unknown message type."

    return response


# 主动发送其他消息的函数
async def send_additional_messages(client):
    await asyncio.sleep(1)  # 模拟一些延迟
    for client in connected_clients:
        character_id = character_objects[client.remote_address]
        # 发送 actionList 消息
        message = create_message(
            character_id,
            "actionList",
            6,
            command=[
                "goto orchard",
                "pickapple 2",
                "goto mine",
                "gomining 5",
                "goto fishing",
                "gofishing 5",
                "goto home",
                "sleep 8",
            ],
        )
        await client.send(json.dumps(message))
        # # 发送 singleAction 消息
        # message = create_message(
        #     character_id, "singleAction", 2, command="goto orchard"
        # )
        # await client.send(json.dumps(message))


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
        # 创建接收消息的任务
        receive_task = asyncio.create_task(receive_messages(websocket))
        # 创建发送额外消息的任务
        send_task = asyncio.create_task(send_additional_messages(websocket))

        # 等待两个任务完成
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


async def main():
    host = "localhost"
    port = 6789
    server = await websockets.serve(handler, host, port)
    print(f"WebSocket server started at ws://{host}:{port}")
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
