import sys

sys.path.append(".")

import yaml
import asyncio
import websockets
import ssl
import json
import os
from loguru import logger
from websocket_server.character_manager import CharacterManager
from websocket_server.web_monitor.routes import WebMonitor
from graph_instance import LangGraphInstance
from conversation_instance import ConversationInstance


class ConfigLoader:
    def __init__(self, environment):
        config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
        with open(config_path, "r") as file:
            self.config = yaml.safe_load(file)[environment]

    def get(self, key):
        return self.config.get(key)


class ConfigLoader:
    def __init__(self, environment):
        config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
        with open(config_path, "r") as file:
            self.config = yaml.safe_load(file)[environment]

    def get(self, key):
        return self.config.get(key)


class AI_WS_Server:
    def __init__(self, config):
        self.character_manager = CharacterManager(timeout=60)
        self.web_monitor = WebMonitor(self.character_manager)
        self.config = config

    async def handler(self, websocket, path):
        character_id = None
        try:
            success, character_id, response = await self.initialize_connection(
                websocket
            )
            await websocket.send(response)
            if not success:
                logger.warning(
                    f"🔗 Failed to connect to remote websocket: {websocket.remote_address}"
                )
                return

            logger.info(
                f"🔗 Successfully connected to remote websocket: {websocket.remote_address}"
            )
            character = self.character_manager.get_character(character_id)
            agent_instance = character.agent_instance
            # conversation_instance = character.conversation_instance

            character.log_message("received", response)

            character.log_message("received", response)

            # 处理消息循环
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)

                    character.log_message("sent", message)

                    # 处理心跳消息
                    if data.get("messageName") == "heartbeat":
                        character.update_heartbeat()
                        heartbeat_response = self.create_message(
                            character_id, "heartbeat", 0, **{"status": "ok"}
                        )
                        await websocket.send(heartbeat_response)
                        character.log_message("received", heartbeat_response)
                        continue

                    else:  # 处理其他消息：放到对应agent和conversation agent的消息队列
                        message_queue = agent_instance.state["message_queue"]
                        await message_queue.put(data)

                    # logger.info(
                    #     f"🧾 User {agent_instance.user_id} message_queue: {message_queue}"
                    # )

                    # # 处理消息：对话系统
                    # await conversation_instance.listener(message)

                except websockets.ConnectionClosed as e:
                    logger.warning(f"🔗 Connection closed from {character_id}")
                    break
                except Exception as e:
                    logger.error(f"❌ Error in message loop: {str(e)}")
                    break
        finally:
            self.character_manager.host_character(character_id)
            logger.info(f"🧹 Cleaned up resources for Character {character_id}")

    async def initialize_connection(self, websocket):
        init_message = await websocket.recv()
        init_data = json.loads(init_message)
        character_id = init_data.get("characterId")
        message_name = init_data.get("messageName")
        message_code = init_data.get("messageCode")

        if not character_id:
            return (
                False,
                character_id,
                self.create_message(
                    character_id,
                    message_name,
                    message_code,
                    **{"result": False, "msg": "character init failed"},
                ),
            )

        if self.character_manager.has_character(character_id):
            return (
                False,
                character_id,
                self.create_message(
                    character_id,
                    message_name,
                    message_code,
                    **{"result": False, "msg": "character ID is active"},
                ),
            )

        if self.character_manager.has_hosted_character(character_id):
            self.character_manager.unhost_character(character_id)

        agent_instance = LangGraphInstance(character_id, websocket)
        conversation_instance = None  # ConversationInstance(character_id, websocket)

        self.character_manager.add_character(
            character_id, agent_instance, conversation_instance
        )

        self.character_manager.get_character(character_id).log_message(
            "sent", init_message
        )

        return (
            True,
            character_id,
            self.create_message(
                character_id,
                message_name,
                message_code,
                **{"result": True, "msg": "character init success"},
            ),
        )

    def create_message(self, character_id, message_name, message_code, **kwargs):
        return json.dumps(
            {
                "characterId": character_id,
                "messageCode": message_code,
                "messageName": message_name,
                "data": kwargs,
            }
        )

    async def run(self):
        # 启动心跳监控
        if self.config.get("monitor_trigger"):
            await self.character_manager.start_monitoring()

        # 启动 HTTP 监控服务器
        if self.config.get("dashboard_trigger"):
            http_host = self.config.get("http_monitor_host")
            http_port = self.config.get("http_monitor_port")
            await self.web_monitor.setup(host=http_host, port=http_port)
            logger.info(f"🌐 HTTP Monitor started at http://{http_host}:{http_port}")

        ws_host = self.config.get("websocket_host")
        ws_port = self.config.get("websocket_port")

        # 根据开关确定是否用SSL/TLS
        if self.config.get("ssl_trigger"):
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(
                certfile=self.config.get("ssl_certfile"),
                keyfile=self.config.get("ssl_keyfile"),
            )
            server = await websockets.serve(
                self.handler, ws_host, ws_port, ssl=ssl_context
            )

            logger.warning(f"🔗 WebSocket server started at wss://{ws_host}:{ws_port}")
        else:
            server = await websockets.serve(self.handler, ws_host, ws_port)
            logger.warning(f"🔗 WebSocket server started at ws://{ws_host}:{ws_port}")

        await server.wait_closed()


def main():
    environment = "production" if sys.platform.startswith("linux") else "development"
    config = ConfigLoader(environment)
    server = AI_WS_Server(config)
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
