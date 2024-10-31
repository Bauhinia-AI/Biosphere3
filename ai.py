import asyncio
import websockets
import ssl
import json
import sys
from loguru import logger
from websocket_server.task_manager import OrphanedTaskManager
from websocket_server.heartbeat_manager import HeartbeatManager
from websocket_server.web_monitor.routes import WebMonitor
from graph_instance import LangGraphInstance

# 全局实例
character_objects = {}  # websocket -> agent_instance
orphaned_task_manager = OrphanedTaskManager()
heartbeat_manager = HeartbeatManager(timeout=60)  # 60秒超时


async def handler(websocket, path):
    character_id = None
    try:
        success, character_id, response = await initialize_connection(websocket)
        await websocket.send(json.dumps(response))
        if not success:
            logger.error(f"❌ Initialize failed from {websocket.remote_address}")
            return

        logger.info(f"✅ Initialized successfully from {websocket.remote_address}")
        agent_instance = character_objects[websocket.remote_address]

        # 设置心跳超时回调
        async def timeout_callback():
            if websocket.remote_address in character_objects:
                logger.info(f"🤖 {character_id} timeout, add tasks to manager...")
                await orphaned_task_manager.add_orphaned_tasks(
                    agent_instance.user_id, agent_instance.tasks
                )
                del character_objects[websocket.remote_address]

        # 添加心跳监控
        heartbeat_manager.add_client(character_id, timeout_callback)
        heartbeat_manager.update_heartbeat(character_id)

        # 处理消息循环
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)

                # 处理心跳消息
                if data.get("messageName") == "heartbeat":
                    heartbeat_manager.update_heartbeat(character_id)
                    await websocket.send(
                        json.dumps(
                            create_message(
                                character_id, "heartbeat", 0, **{"status": "ok"}
                            )
                        )
                    )
                    continue

                # 处理其他消息：放到对应agent的消息队列
                message_queue = agent_instance.state["message_queue"]
                async with agent_instance.state_lock:
                    await message_queue.put(data)
                logger.info(
                    f"🧾 User {agent_instance.user_id} message_queue: {message_queue}"
                )
            except websockets.ConnectionClosed:
                logger.warning(f"❌ Connection closed from {websocket.remote_address}")
                raise
            except Exception as e:
                logger.error(f"❌ Error processing message: {str(e)}")
                break
    except Exception as e:
        logger.error(f"❌ Error in main loop: {str(e)}")
    finally:
        if character_id:
            heartbeat_manager.remove_client(character_id)
        if websocket.remote_address in character_objects:
            del character_objects[websocket.remote_address]


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

    # 恢复或创建agent实例
    if await orphaned_task_manager.has_orphaned_tasks(character_id):
        existing_tasks = await orphaned_task_manager.get_tasks(character_id)
        agent_instance = LangGraphInstance(character_id, websocket)
        agent_instance.tasks = existing_tasks
    else:
        agent_instance = LangGraphInstance(character_id, websocket)

    character_objects[websocket_address] = agent_instance

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


async def main():
    # 启动心跳监控
    await heartbeat_manager.start_monitoring()

    # 启动 HTTP 监控服务器
    web_monitor = WebMonitor(heartbeat_manager, orphaned_task_manager)
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
