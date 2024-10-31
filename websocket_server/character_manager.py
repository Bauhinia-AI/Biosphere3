import sys

sys.path.append("..")
from graph_instance import LangGraphInstance
from typing import Dict, Optional


class CharacterManager:
    def __init__(self):
        self._characters: Dict[int, LangGraphInstance] = {}

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
