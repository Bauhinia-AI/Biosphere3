import asyncio
import websockets
import json


# 定义不同类型的消息
def create_message(message_name, message_code, command_list=None):
    message = {
        "characterId": 1,
        "messageCode": message_code,
        "messageName": message_name,
        "data": {"msg": f"client request {message_name}"},
    }
    if command_list:
        message["data"]["command"] = command_list  # 在 data 中添加 command 字段
    return message


# 各种请求的消息，编号从 1 开始
MESSAGES = {
    "connectionInit": create_message("connectionInit", 1),
    "singleAction": create_message("singleAction", 2),
    "actionResult": create_message("actionResult", 3),
    "getInfo": create_message("getInfo", 4),
    "getGameTime": create_message("getGameTime", 5),
    "actionList": lambda command_list: create_message(
        "actionList", 6, command_list
    ),  # 动态生成 actionList 消息
}


# 向服务器发送消息的函数
async def send_message(websocket, message):
    await websocket.send(json.dumps(message))
    print(f"Sent: {message}")


# 处理从服务器接收的消息
async def receive_message(websocket):
    try:
        message = await websocket.recv()
        print(f"Received: {message}")
    except websockets.ConnectionClosed:
        print("Connection closed while receiving messages.")


# 客户端主函数
async def client():
    uri = "ws://localhost:6789"
    async with websockets.connect(uri) as websocket:
        print("Connected to AI server...")

        # 发送 connectionInit 消息
        await send_message(websocket, MESSAGES["connectionInit"])
        await receive_message(websocket)  # 接收 connectionInit 的响应

        # 开始监听AI端的消息
        while True:
            await receive_message(websocket)
            # 这里可以根据接收到的消息类型进行相应的处理
            # 例如，处理 singleAction, actionResult 等消息

if __name__ == "__main__":
    asyncio.run(client())
