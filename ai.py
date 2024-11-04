import asyncio
import websockets
import ssl
import json
import sys
from loguru import logger
from websocket_server.task_manager import OrphanedTaskManager
from websocket_server.character_manager import CharacterManager, Character
from websocket_server.web_monitor.routes import WebMonitor
from graph_instance import LangGraphInstance

# 全局实例
character_manager = CharacterManager(timeout=60)
orphaned_task_manager = OrphanedTaskManager()


async def handler(websocket, path):
    character_id = None
    try:
        success, character_id, response = await initialize_connection(websocket)
        await websocket.send(response)
        if not success:
            logger.warning(
                f"🔗 Failed to connect to remote websocket: {websocket.remote_address}"
            )
            return

        logger.info(
            f"🔗 Successfully connected to remote websocket: {websocket.remote_address}"
        )
        character = character_manager.get_character(character_id)
        agent_instance = character.instance

        # 处理消息循环
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)

                # 处理心跳消息
                if data.get("messageName") == "heartbeat":
                    character.update_heartbeat()
                    await websocket.send(
                        create_message(character_id, "heartbeat", 0, **{"status": "ok"})
                    )
                    continue

                # 处理其他消息：放到对应agent的消息队列
                message_queue = agent_instance.state["message_queue"]
                async with agent_instance.state_lock:
                    await message_queue.put(data)
                logger.info(
                    f"🧾 User {agent_instance.user_id} message_queue: {message_queue}"
                )
            except websockets.ConnectionClosed as e:
                logger.warning(f"🔗 Connection closed from {websocket.remote_address}")
                break
            except Exception as e:
                logger.error(f"❌ Error in message loop: {str(e)}")
                break
    finally:
        character_manager.host_character(character_id)
        logger.info(f"🧹 Cleaned up resources for Character {character_id}")


async def initialize_connection(websocket):
    init_message = await websocket.recv()
    init_data = json.loads(init_message)
    character_id = init_data.get("characterId")
    message_name = init_data.get("messageName")
    message_code = init_data.get("messageCode")

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

    if character_manager.has_character(character_id):
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

    agent_instance = LangGraphInstance(character_id, websocket)

    async def timeout_callback():
        if character_manager.has_character(character_id):
            await orphaned_task_manager.add_orphaned_tasks(
                agent_instance.user_id, agent_instance.tasks
            )

    character_manager.add_character(character_id, agent_instance, timeout_callback)

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
    return json.dumps(
        {
            "characterId": character_id,
            "messageCode": message_code,
            "messageName": message_name,
            "data": kwargs,
        }
    )


async def main():
    # 启动心跳监控
    await character_manager.start_monitoring()

    # 启动 HTTP 监控服务器
    web_monitor = WebMonitor(character_manager, orphaned_task_manager)
    await web_monitor.setup(host="localhost", port=8000)
    logger.info(f"🌐 HTTP Monitor started at http://localhost:8000")

    # if is linux
    if sys.platform.startswith("linux"):
        host = "0.0.0.0"
        port = 8080
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(
            certfile="/etc/ssl/certs/bio3.crt", keyfile="/etc/ssl/certs/bio3.key"
        )
        server = await websockets.serve(handler, host, port, ssl=ssl_context)
        logger.warning(f"🔗 WebSocket server started at ws://{host}:{port}")
        await server.wait_closed()
    elif sys.platform.startswith("darwin"):
        host = "localhost"
        port = 6789
        server = await websockets.serve(handler, host, port)
        logger.warning(f"🔗 WebSocket server started at ws://{host}:{port}")
        await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
