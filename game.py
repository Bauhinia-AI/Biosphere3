import asyncio
import websockets
import json
from loguru import logger


class TestClient:
    def __init__(self, uri="wss://47.95.21.135:8080", character_id=29):
        self.uri = uri
        self.character_id = character_id
        self.websocket = None
        self.running = True

    def create_message(self, message_name, message_code=0, **kwargs):
        return {
            "characterId": self.character_id,
            "messageCode": message_code,
            "messageName": message_name,
            "data": kwargs,
        }

    async def connect(self):
        """建立连接并初始化"""
        try:
            self.websocket = await websockets.connect(self.uri)
            logger.info(f"Connected to {self.uri}")

            # 发送初始化消息
            init_message = self.create_message(
                message_name="connectionInit", message_code=1
            )
            await self.websocket.send(json.dumps(init_message))
            response = await self.websocket.recv()
            logger.info(f"Initialization response: {response}")

            return True
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            return False

    async def heartbeat(self):
        """发送心跳"""
        while self.running:
            try:
                if self.websocket and not self.websocket.closed:
                    heartbeat_message = self.create_message("heartbeat")
                    await self.websocket.send(json.dumps(heartbeat_message))
                    response = await self.websocket.recv()
                    logger.debug(f"Heartbeat response: {response}")
                await asyncio.sleep(30)  # 每30秒发送一次心跳
            except Exception as e:
                logger.error(f"Heartbeat error: {str(e)}")
                break

    async def run(self):
        """运行测试客户端"""
        if not await self.connect():
            return

        try:
            heartbeat_task = asyncio.create_task(self.heartbeat())
            await asyncio.sleep(120)  # 运行2分钟

        except Exception as e:
            logger.error(f"Error in client: {str(e)}")
        finally:
            self.running = False
            if heartbeat_task:
                heartbeat_task.cancel()
            if self.websocket:
                await self.websocket.close()


async def test_multiple_clients():
    """测试多个客户端"""
    clients = [TestClient(character_id=29 + i) for i in range(3)]

    tasks = [client.run() for client in clients]
    await asyncio.gather(*tasks)


async def main():
    """主测试函数"""
    logger.info("Starting WebSocket client tests...")

    # # 测试多客户端
    logger.info("=== Testing multiple clients ===")
    await test_multiple_clients()


if __name__ == "__main__":
    asyncio.run(main())
