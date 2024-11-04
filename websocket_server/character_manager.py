import sys

sys.path.append("..")
import time
import asyncio
from typing import Dict, Optional, Callable, Coroutine, Any
from graph_instance import LangGraphInstance
from loguru import logger


class Character:
    def __init__(self, instance: LangGraphInstance):
        self.instance = instance
        self.last_heartbeat = time.time()
        self.heartbeat_count = 1
        self.callback: Optional[Callable[[], Coroutine[Any, Any, None]]] = None

    def update_heartbeat(self):
        self.last_heartbeat = time.time()
        self.heartbeat_count += 1


class CharacterManager:
    def __init__(self, timeout: int = 60):
        self.timeout: int = timeout
        self._monitor_task: Optional[asyncio.Task] = None
        self.start_time: float = time.time()
        self._characters: Dict[int, Character] = {}  # 当前活跃的角色实例
        self._hosted_characters: Dict[int, Character] = {}  # 当前托管的角色实例

    """添加一个新的角色实例"""
    def add_character(
        self,
        character_id: int,
        agent_instance: LangGraphInstance,
        callback: Optional[Callable[[], Coroutine[Any, Any, None]]] = None
    ) -> None:
        self._characters[character_id] = Character(agent_instance)
        if callback:
            self._characters[character_id].callback = callback

    """托管一个角色实例"""
    def host_character(self, character_id: int) -> None:
        self._hosted_characters[character_id] = self._characters[character_id]
        self._characters.pop(character_id, None)

    """移除一个角色实例"""
    def remove_character(self, character_id: int) -> None:
        self._characters.pop(character_id, None)
        self._hosted_characters.pop(character_id, None)

    """获取一个角色实例"""
    def get_character(self, character_id: int) -> Optional[Character]:
        if character_id in self._hosted_characters:
            return self._hosted_characters[character_id]
        return self._characters.get(character_id, None)

    """检查角色实例是否存在"""
    def has_character(self, character_id: int) -> bool:
        return character_id in self._characters

    """检查托管角色实例是否存在"""
    def has_hosted_character(self, character_id: int) -> bool:
        return character_id in self._hosted_characters

    """启动心跳监控"""
    async def start_monitoring(self) -> None:
        self._monitor_task = asyncio.create_task(self._check_heartbeats())
        logger.info("🫀 Heartbeat monitoring started")

    """检查心跳状态"""
    async def _check_heartbeats(self) -> None:
        while True:
            logger.info("🔍 Performing heartbeat check...")
            for character_id, character in self._characters.items():
                if time.time() - character.last_heartbeat > self.timeout:
                    logger.error(f"💔 Character {character_id} heartbeat timeout")
                    # 执行超时回调
                    if character.callback:
                        await character.callback()
                    self.host_character(character_id)
            await asyncio.sleep(self.timeout / 2)

    async def get_status(self) -> Dict[str, Any]:
        """获取心跳管理器的状态信息"""
        active_characters = [
            {
                "character_id": character_id,
                "status": "active",
                "last_heartbeat_time": time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(character.last_heartbeat)
                ),
                "heartbeat_count": character.heartbeat_count,
                "has_callback": character.callback is not None
            }
            for character_id, character in self._characters.items()
        ]

        hosted_characters = [
            {
                "character_id": character_id,
                "status": "hosted",
                "last_heartbeat_time": time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(character.last_heartbeat)
                ),
                "heartbeat_count": character.heartbeat_count,
                "has_callback": character.callback is not None
            }
            for character_id, character in self._hosted_characters.items()
        ]

        return {
            "monitor_status": {
                "uptime_seconds": f"{int(time.time() - self.start_time)} seconds",
                "timeout_setting": f"{self.timeout} seconds",
                "check_interval": f"{self.timeout // 2} seconds",
                "total_count": len(self._characters),
                "active_count": len(active_characters),
                "hosted_count": len(hosted_characters),
            },
            "clients": {
                "active_characters": active_characters,
                "hosted_characters": hosted_characters,
            },
        }
