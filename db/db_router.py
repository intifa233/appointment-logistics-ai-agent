from .base import SessionManager
from .repositories import TeaMasterRepository, TeaRoomRepository, InventoryRepository, KnowledgeRepository, UserBehaviorRepository
from typing import Optional


class DatabaseRouter:
    """
    数据库路由器

    职责：
    1. 管理数据库连接和会话
    2. 提供统一的数据访问入口
    3. 协调各个Repository的操作
    """

    def __init__(self, db_path: str = 'sqlite:///data/tea_house.db'):
        """
        初始化数据库路由器

        Args:
            db_path: 数据库连接路径
        """
        self.session_manager = SessionManager(db_path)

        # 初始化各个Repository
        self.tea_master_repo = TeaMasterRepository(self.session_manager)
        self.tea_room_repo = TeaRoomRepository(self.session_manager)
        self.inventory_repo = InventoryRepository(self.session_manager)
        self.knowledge_repo = KnowledgeRepository(self.session_manager)
        self.user_behavior_repo = UserBehaviorRepository(self.session_manager)

    @property
    def tea_masters(self) -> TeaMasterRepository:
        """获取茶艺师数据仓库"""
        return self.tea_master_repo

    @property
    def tea_rooms(self) -> TeaRoomRepository:
        """获取茶室数据仓库"""
        return self.tea_room_repo

    @property
    def inventory(self) -> InventoryRepository:
        """获取库存数据仓库"""
        return self.inventory_repo

    @property
    def knowledge(self) -> KnowledgeRepository:
        """获取知识库数据仓库"""
        return self.knowledge_repo

    @property
    def user_behavior(self) -> UserBehaviorRepository:
        """获取用户行为数据仓库"""
        return self.user_behavior_repo

    def close(self):
        """关闭数据库连接"""
        self.session_manager.close()


# 为了兼容性，保留原有的类名
class TeaMasterDBRouter:
    """
    茶艺师数据库路由器（兼容性类）

    为保持向后兼容，继续支持原有的接口
    """

    def __init__(self, db_type='local', **kwargs):
        self.db_router = DatabaseRouter(**kwargs)
        self.tea_master_repo = self.db_router.tea_masters

    # 茶艺师相关方法
    def add_tea_master(self, name, gender=None, specialty=None) -> None:
        return self.tea_master_repo.add_tea_master(name, gender, specialty)

    def get_tea_master_by_name(self, name: str):
        return self.tea_master_repo.get_tea_master_by_name(name)

    def get_tea_master_by_id(self, tea_master_id: int):
        return self.tea_master_repo.get_tea_master_by_id(tea_master_id)

    def get_all_tea_masters(self):
        return self.tea_master_repo.get_all_tea_masters()

    def get_all_specialties(self):
        return self.tea_master_repo.get_all_specialties()

    # 排班相关方法
    def add_schedule(self, tea_master_id: int, start_time, end_time, status, appointment_id=None) -> None:
        return self.tea_master_repo.add_schedule(tea_master_id, start_time, end_time, status, appointment_id)

    def get_tea_master_schedules(self, tea_master_id: int, date):
        return self.tea_master_repo.get_tea_master_schedules(tea_master_id, date)

    def is_tea_master_available(self, tea_master_id: int, start_time, end_time) -> bool:
        return self.tea_master_repo.is_tea_master_available(tea_master_id, start_time, end_time)

    def get_tea_masters_by_gender(self, gender: str):
        return self.tea_master_repo.get_tea_masters_by_gender(gender)


class TeaRoomDBRouter:
    """
    茶室数据库路由器（兼容性类）

    为保持向后兼容，继续支持原有的接口
    """

    def __init__(self, db_type='local', **kwargs):
        self.db_router = DatabaseRouter(**kwargs)
        self.tea_room_repo = self.db_router.tea_rooms

    def add_room(self, name, room_type=None, capacity=None, equipment=None) -> None:
        return self.tea_room_repo.add_room(name, room_type, capacity, equipment)

    def get_room_by_id(self, room_id: int):
        return self.tea_room_repo.get_room_by_id(room_id)

    def get_all_rooms(self):
        return self.tea_room_repo.get_all_rooms()

    def get_rooms_by_type(self, room_type: str):
        return self.tea_room_repo.get_rooms_by_type(room_type)

    def add_room_schedule(self, room_id: int, start_time, end_time, status, appointment_id=None) -> None:
        return self.tea_room_repo.add_room_schedule(room_id, start_time, end_time, status, appointment_id)

    def get_room_schedules(self, room_id: int, date):
        return self.tea_room_repo.get_room_schedules(room_id, date)

    def is_room_available(self, room_id: int, start_time, end_time) -> bool:
        return self.tea_room_repo.is_room_available(room_id, start_time, end_time)


class InventoryDBRouter:
    """
    库存数据库路由器（兼容性类）

    为保持向后兼容，继续支持原有的接口
    """

    def __init__(self, db_type='local', **kwargs):
        self.db_router = DatabaseRouter(**kwargs)
        self.inventory_repo = self.db_router.inventory

    def add_item(self, name, category=None, unit=None, stock_quantity=0, reorder_threshold=0, unit_price=None) -> None:
        return self.inventory_repo.add_item(name, category, unit, stock_quantity, reorder_threshold, unit_price)

    def get_item_by_id(self, item_id: int):
        return self.inventory_repo.get_item_by_id(item_id)

    def get_all_items(self):
        return self.inventory_repo.get_all_items()

    def adjust_stock(self, item_id: int, delta: float) -> bool:
        return self.inventory_repo.adjust_stock(item_id, delta)

    def get_low_stock_items(self):
        return self.inventory_repo.get_low_stock_items()


class KnowledgeDBRouter:
    """
    知识库数据库路由器（兼容性类）

    为保持向后兼容，继续支持原有的接口
    """

    def __init__(self, db_type='local', **kwargs):
        self.db_router = DatabaseRouter(**kwargs)
        self.knowledge_repo = self.db_router.knowledge

    def add_document(self, content: str, category: str, keywords=None, embedding=None) -> int:
        return self.knowledge_repo.add_document(content, category, keywords, embedding)

    def get_document(self, doc_id: int):
        return self.knowledge_repo.get_document(doc_id)

    def get_all_documents(self, include_inactive: bool = False):
        return self.knowledge_repo.get_all_documents(include_inactive)

    def update_document(self, doc_id: int, content=None, category=None, keywords=None, embedding=None) -> bool:
        return self.knowledge_repo.update_document(doc_id, content, category, keywords, embedding)

    def delete_document(self, doc_id: int, soft_delete: bool = True) -> bool:
        return self.knowledge_repo.delete_document(doc_id, soft_delete)

    def search_documents_by_category(self, category: str):
        return self.knowledge_repo.search_documents_by_category(category)

    def search_documents_by_keywords(self, keywords):
        return self.knowledge_repo.search_documents_by_keywords(keywords)

    def get_all_categories(self):
        return self.knowledge_repo.get_all_categories()

    def get_documents_count(self) -> int:
        return self.knowledge_repo.get_documents_count()


class UserBehaviorDBRouter:
    """
    用户行为数据库路由器（兼容性类）

    为保持向后兼容，继续支持原有的接口
    """

    def __init__(self, db_type='local', **kwargs):
        self.db_router = DatabaseRouter(**kwargs)
        self.user_behavior_repo = self.db_router.user_behavior

    def record_behavior(self, user_id: str, action_type: str, action_data=None, tea_master_id=None, session_id=None) -> int:
        return self.user_behavior_repo.record_behavior(user_id, action_type, action_data, tea_master_id, session_id)

    def get_user_behaviors(self, user_id: str, action_type=None, days_back=None):
        return self.user_behavior_repo.get_user_behaviors(user_id, action_type, days_back)

    def get_user_preferences(self, user_id: str):
        return self.user_behavior_repo.get_user_preferences(user_id)

    def update_user_preference(self, user_id: str, preference_type: str, preference_value: str, confidence_score: int = 1) -> bool:
        return self.user_behavior_repo.update_user_preference(user_id, preference_type, preference_value, confidence_score)
