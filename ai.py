import asyncio
import websockets
import json

# 记录连接到AI端的所有托管游戏玩家
connected_clients = set()

# 模拟数据库
fake_db = {
    1: {"name": "PlayerOne", "level": 5},
    2: {"name": "PlayerTwo", "level": 3},
}

# 维护一个字典，将character_id映射到用户对象
character_objects = {}

# 尝试从数据库中获取用户信息并创建对象
def create_character_object(character_id, websocket_address):
    user_info = fake_db.get(character_id)
    if user_info:
        # 创建一个用户对象
        character_object = {
            "characterId": character_id,
            "name": user_info["name"],
            "level": user_info["level"],
            "websocket": websocket_address,
        }
        # 将对象存储在字典中
        character_objects[character_id] = character_object
        return character_object
    return None

# 处理游戏端发送的消息
async def receive_messages(websocket):
    try:
        async for message in websocket:
            print(f"Received message from game endpoint: {message}")
            response = handle_message(json.loads(message), websocket.remote_address)
            await websocket.send(json.dumps(response))
    except websockets.ConnectionClosed:
        print("Connection closed while receiving messages.")


# 根据消息类型生成响应
def handle_message(message, websocket_address):
    message_name = message.get("messageName")
    character_id = message.get("characterId")
    message_code = message.get("messageCode")
    response = {
        "characterId": character_id,
        "messageCode": message_code,
        "messageName": message_name,
        "data": {},
    }

    if message_name == "connectionInit":
        character_object = create_character_object(character_id, websocket_address)
        if character_object:
            response["data"] = {"result": True, "msg": "character init success"}
        else:
            response["data"] = {"result": False, "msg": "character init failed"}
    else:
        response["data"]["msg"] = "Unknown message type."

    return response


# # 主动发送其他消息的函数
# async def send_additional_messages(client):
#     await asyncio.sleep(1)  # 模拟一些延迟
#     for client in connected_clients:
#         # 发送 singleAction 消息
#         message = create_message("singleAction", 2)
#         await client.send(json.dumps(message))
#         # 发送 actionResult 消息
#         message = create_message("actionResult", 3)
#         await client.send(json.dumps(message))
#         # 发送 getInfo 消息
#         message = create_message("getInfo", 4)
#         await client.send(json.dumps(message))
#         # 发送 getGameTime 消息
#         message = create_message("getGameTime", 5)
#         await client.send(json.dumps(message))


# 创建消息的辅助函数
def create_message(message_name, message_code):
    return {
        "characterId": 1,
        "messageCode": message_code,
        "messageName": message_name,
        "data": {"msg": f"server request {message_name}"},
    }


# 处理游戏端连接
async def handler(websocket, path):
    connected_clients.add(websocket)
    print(
        f"Client connected from {websocket.remote_address}. Total connected clients: {len(connected_clients)}"
    )
    try:
        await receive_messages(websocket)
    except websockets.ConnectionClosed:
        print(f"Connection closed from {websocket.remote_address}")
    finally:
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
