import asyncio
import websockets
import ssl
import json
import sys
from collections import defaultdict
from graph_instance import LangGraphInstance
from loguru import logger

# websocket + character_id -> agent_instance
character_objects = {}

# 使用 defaultdict 初始化 action_results
action_results = defaultdict(list)


async def handler(websocket, path):
    try:
        success, character_id, response = await initialize_connection(websocket)
        await websocket.send(json.dumps(response))
        if not success:
            logger.error(
                f"❌ Failed to initialize websocket connection from {websocket.remote_address}"
            )
            return
        logger.info(
            f"✅ Successfully initialized websocket connection from {websocket.remote_address}"
        )
        agent_instance = character_objects[
            construct_websocket_key(websocket.remote_address, character_id)
        ]
        await agent_instance.task
    except websockets.ConnectionClosed:
        logger.warning(f"❌ Connection closed from {websocket.remote_address}")
    finally:
        if (
            construct_websocket_key(websocket.remote_address, character_id)
            in character_objects
        ):
            del character_objects[
                construct_websocket_key(websocket.remote_address, character_id)
            ]


async def initialize_connection(websocket):
    init_message = await websocket.recv()
    init_data = json.loads(init_message)
    character_id = init_data.get("characterId")
    message_name = init_data.get("messageName")
    message_code = init_data.get("messageCode")
    websocket_address = websocket.remote_address

    if not character_id:
        return (
            False,
            character_id,
            create_message(
                character_id,
                message_name,
                message_code,
                **{"result": False, "msg": "character init failed"},
            ),
        )

    if character_id in [agent.user_id for agent in character_objects.values()]:
        return (
            False,
            character_id,
            create_message(
                character_id,
                message_name,
                message_code,
                **{"result": False, "msg": "character ID is already in use"},
            ),
        )

    # 这时初始化一个agent实例
    agent_instance = LangGraphInstance(character_id, websocket)
    character_objects[construct_websocket_key(websocket_address, character_id)] = (
        agent_instance
    )

    return (
        True,
        character_id,
        create_message(
            character_id,
            message_name,
            message_code,
            **{"result": True, "msg": "character init success"},
        ),
    )


# 创建消息的辅助函数
def create_message(character_id, message_name, message_code, **kwargs):
    return {
        "characterId": character_id,
        "messageCode": message_code,
        "messageName": message_name,
        "data": kwargs,
    }


# 构造websocket key
def construct_websocket_key(websocket_address, character_id):
    return f"{websocket_address}:{character_id}"


async def main():
    # if is linux
    if sys.platform.startswith("linux"):
        host = "0.0.0.0"
        port = 8080
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(
            certfile="/etc/ssl/certs/bio3.crt", keyfile="/etc/ssl/certs/bio3.key"
        )
        server = await websockets.serve(handler, host, port, ssl=ssl_context)
        logger.info(f"🔗 WebSocket server started at ws://{host}:{port}")
        await server.wait_closed()
    elif sys.platform.startswith("darwin"):
        host = "localhost"
        port = 6789
        server = await websockets.serve(handler, host, port)
        logger.info(f"🔗 WebSocket server started at ws://{host}:{port}")
        await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
