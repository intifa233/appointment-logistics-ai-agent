"""
Repositories Module

数据访问对象模块，包含：
- 茶艺师数据仓库
- 茶室数据仓库
- 库存数据仓库
- 知识库数据仓库
- 用户行为数据仓库
"""

from .tea_master_repository import TeaMasterRepository
from .tea_room_repository import TeaRoomRepository
from .inventory_repository import InventoryRepository
from .knowledge_repository import KnowledgeRepository
from .user_behavior_repository import UserBehaviorRepository

__all__ = [
    'TeaMasterRepository',
    'TeaRoomRepository',
    'InventoryRepository',
    'KnowledgeRepository',
    'UserBehaviorRepository'
]
