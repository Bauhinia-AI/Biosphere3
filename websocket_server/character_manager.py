import sys

sys.path.append("..")
import time
import asyncio
from typing import Dict, Optional, Callable, Coroutine, Any
from graph_instance import LangGraphInstance
from loguru import logger


class CharacterManager:
    def __init__(self, timeout: int = 60):
        self._characters: Dict[int, LangGraphInstance] = {}
        self.timeout: int = timeout
        self.last_heartbeat: Dict[int, float] = {}
        self.heartbeat_counts: Dict[int, int] = {}
        self.callbacks: Dict[int, Callable[[], Coroutine[Any, Any, None]]] = {}
        self._monitor_task: Optional[asyncio.Task] = None
        self.start_time: float = time.time()

    def add_character(
        self, character_id: int, agent_instance: LangGraphInstance
    ) -> None:
        """添加一个新的角色实例"""
        self._characters[character_id] = agent_instance

    def remove_character(self, character_id: int) -> None:
        """移除一个角色实例"""
        if self.has_character(character_id):
            del self._characters[character_id]

    def get_character(self, character_id: int) -> Optional[LangGraphInstance]:
        """获取一个角色实例"""
        return self._characters.get(character_id, None)

    def has_character(self, character_id: int) -> bool:
        """检查角色实例是否存在"""
        return character_id in self._characters

    def add_heartbeat(
        self,
        character_id: int,
        callback: Optional[Callable[[], Coroutine[Any, Any, None]]] = None,
    ) -> None:
        """添加新的客户端心跳监控"""
        self.last_heartbeat[character_id] = time.time()
        self.heartbeat_counts[character_id] = 1
        if callback:
            self.callbacks[character_id] = callback
        logger.info(f"🧐 Added heartbeat monitoring for character {character_id}")

    def remove_heartbeat(self, character_id: int) -> None:
        """移除客户端心跳监控"""
        self.last_heartbeat.pop(character_id, None)
        self.heartbeat_counts.pop(character_id, None)
        self.callbacks.pop(character_id, None)
        logger.info(f"🙅 Removed heartbeat monitoring for character {character_id}")

    def update_heartbeat(self, character_id: int) -> None:
        """更新心跳时间"""
        self.last_heartbeat[character_id] = time.time()
        self.heartbeat_counts[character_id] = (
            self.heartbeat_counts.get(character_id, 0) + 1
        )

    def is_alive(self, character_id: int) -> bool:
        """检查客户端是否活跃"""
        if character_id not in self.last_heartbeat:
            return False
        return time.time() - self.last_heartbeat[character_id] <= self.timeout

    async def start_monitoring(self) -> None:
        """启动心跳监控"""
        self._monitor_task = asyncio.create_task(self._check_heartbeats())
        logger.info("🫀 Heartbeat monitoring started")

    async def _check_heartbeats(self) -> None:
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
                self.remove_character(character_id)

            await asyncio.sleep(self.timeout / 2)

    async def get_status(self) -> Dict[str, Any]:
        """获取心跳管理器的状态信息"""
        now = time.time()
        monitored_clients = []

        for character_id, last_time in self.last_heartbeat.items():
            is_alive = self.is_alive(character_id)
            client_info = {
                "character_id": character_id,
                "status": "active" if is_alive else "timeout",
                "last_heartbeat_time": time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(last_time)
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
