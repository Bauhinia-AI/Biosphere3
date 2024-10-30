import time
import asyncio
from loguru import logger

class HeartbeatManager:
    def __init__(self, timeout=60):
        self.last_heartbeat = {}  # character_id -> last_heartbeat_time
        self.timeout = timeout
        self._monitor_task = None
        self.callbacks = {}  # character_id -> callback

    async def start_monitoring(self):
        """启动心跳监控"""
        self._monitor_task = asyncio.create_task(self._check_heartbeats())
        logger.info("🫀 Heartbeat monitoring started")

    async def _check_heartbeats(self):
        """检查心跳状态"""
        while True:
            now = time.time()
            dead_connections = []
            
            for character_id, last_time in self.last_heartbeat.items():
                if now - last_time > self.timeout:
                    dead_connections.append(character_id)
            
            for character_id in dead_connections:
                logger.warning(f"🫀 Character {character_id} heartbeat timeout")
                # 执行超时回调
                if character_id in self.callbacks:
                    await self.callbacks[character_id]()
                self.remove_client(character_id)
            
            await asyncio.sleep(self.timeout / 2)

    def update_heartbeat(self, character_id):
        """更新心跳时间"""
        self.last_heartbeat[character_id] = time.time()

    def add_client(self, character_id, callback=None):
        """添加新的客户端监控"""
        self.last_heartbeat[character_id] = time.time()
        if callback:
            self.callbacks[character_id] = callback
        logger.info(f"🧐 Added heartbeat monitoring for character {character_id}")

    def remove_client(self, character_id):
        """移除客户端监控"""
        self.last_heartbeat.pop(character_id, None)
        self.callbacks.pop(character_id, None)
        logger.info(f"🙅 Removed heartbeat monitoring for character {character_id}")

    def is_alive(self, character_id):
        """检查客户端是否活跃"""
        if character_id not in self.last_heartbeat:
            return False
        return time.time() - self.last_heartbeat[character_id] <= self.timeout
