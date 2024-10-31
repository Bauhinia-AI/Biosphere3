import time
import asyncio
from datetime import datetime
from loguru import logger


class HeartbeatManager:
    def __init__(self, timeout=60):
        self.timeout = timeout
        self.last_heartbeat = {}  # character_id -> last_heartbeat_time
        self.callbacks = {}  # character_id -> callback
        self.heartbeat_counts = {}  # character_id -> heartbeat_count
        self._monitor_task = None

        self.start_time = time.time()

    async def get_status(self):
        """获取心跳管理器的状态信息"""
        now = time.time()
        monitored_clients = []

        for character_id, last_time in self.last_heartbeat.items():
            is_alive = self.is_alive(character_id)
            client_info = {
                "character_id": character_id,
                "status": "active" if is_alive else "timeout",
                "last_heartbeat_time": datetime.fromtimestamp(last_time).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "heartbeat_count": self.heartbeat_counts.get(character_id, 0),
                "has_callback": character_id in self.callbacks,
            }
            monitored_clients.append(client_info)

        return {
            "monitor_status": {
                "uptime_seconds": f"{int(now - self.start_time)} seconds",
                "timeout_setting": f"{self.timeout} seconds",
                "check_interval": f"{self.timeout // 2} seconds",
                "total_count": len(self.last_heartbeat),
                "active_count": sum(
                    1 for c in monitored_clients if c["status"] == "active"
                ),
                "timeout_count": sum(
                    1 for c in monitored_clients if c["status"] == "timeout"
                ),
            },
            "clients": {
                "active_clients": [
                    c for c in monitored_clients if c["status"] == "active"
                ],
                "timeout_clients": [
                    c for c in monitored_clients if c["status"] == "timeout"
                ],
            },
        }

    async def start_monitoring(self):
        """启动心跳监控"""
        self._monitor_task = asyncio.create_task(self._check_heartbeats())
        logger.info("🫀 Heartbeat monitoring started")

    async def _check_heartbeats(self):
        """检查心跳状态"""
        while True:
            logger.info("🔍 Performing heartbeat check...")
            now = time.time()
            dead_connections = []

            for character_id, last_time in self.last_heartbeat.items():
                if now - last_time > self.timeout:
                    dead_connections.append(character_id)

            for character_id in dead_connections:
                logger.error(f"💔 Character {character_id} heartbeat timeout")
                # 执行超时回调
                if character_id in self.callbacks:
                    await self.callbacks[character_id]()
                self.remove_client(character_id)

            await asyncio.sleep(self.timeout / 2)

    def update_heartbeat(self, character_id):
        """更新心跳时间"""
        self.last_heartbeat[character_id] = time.time()
        self.heartbeat_counts[character_id] = (
            self.heartbeat_counts.get(character_id, 0) + 1
        )

    def add_client(self, character_id, callback=None):
        """添加新的客户端监控"""
        self.last_heartbeat[character_id] = time.time()
        self.heartbeat_counts[character_id] = 0
        if callback:
            self.callbacks[character_id] = callback
        logger.info(f"🧐 Added heartbeat monitoring for character {character_id}")

    def remove_client(self, character_id):
        """移除客户端监控"""
        self.last_heartbeat.pop(character_id, None)
        self.callbacks.pop(character_id, None)
        self.heartbeat_counts.pop(character_id, None)
        logger.info(f"🙅 Removed heartbeat monitoring for character {character_id}")

    def is_alive(self, character_id):
        """检查客户端是否活跃"""
        if character_id not in self.last_heartbeat:
            return False
        return time.time() - self.last_heartbeat[character_id] <= self.timeout
