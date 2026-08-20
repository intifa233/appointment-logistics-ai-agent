"""
业务服务层模块

包含：
- 知识库服务
- 茶艺师服务
- 茶室服务
- 库存服务
- 预约服务
- 用户行为服务
- 推荐调度服务
- 文本嵌入工具
"""

from .text_embedding import (
    embed_input,
    find_best_match_indices,
    save_tea_master_embeddings,
    load_tea_master_embeddings
)
from .knowledge_service import KnowledgeService
from .tea_master_service import TeaMasterService
from .tea_room_service import TeaRoomService
from .inventory_service import InventoryService
from .appointment_service import AppointmentService
from .user_behavior_service import UserBehaviorService
from .recommendation_service import RecommendationService

__all__ = [
    'embed_input',
    'find_best_match_indices',
    'save_tea_master_embeddings',
    'load_tea_master_embeddings',
    'KnowledgeService',
    'TeaMasterService',
    'TeaRoomService',
    'InventoryService',
    'AppointmentService',
    'UserBehaviorService',
    'RecommendationService'
]
