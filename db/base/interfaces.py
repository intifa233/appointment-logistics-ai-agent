from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime


class BaseTeaMasterRepository(ABC):
    """
    茶艺师数据访问抽象接口

    定义茶艺师相关的所有数据操作方法
    """

    @abstractmethod
    def add_tea_master(self, name: str, gender: Optional[str] = None, specialty: Optional[str] = None) -> int:
        """添加茶艺师"""
        pass

    @abstractmethod
    def get_tea_master_by_id(self, tea_master_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取茶艺师信息"""
        pass

    @abstractmethod
    def get_tea_master_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据姓名获取茶艺师信息"""
        pass

    @abstractmethod
    def get_all_tea_masters(self) -> List[Dict[str, Any]]:
        """获取所有茶艺师"""
        pass

    @abstractmethod
    def get_all_specialties(self) -> List[str]:
        """获取所有茶艺师的专长"""
        pass

    @abstractmethod
    def update_tea_master(self, tea_master_id: int, **updates) -> bool:
        """更新茶艺师信息"""
        pass

    @abstractmethod
    def delete_tea_master(self, tea_master_id: int) -> bool:
        """删除茶艺师"""
        pass

    @abstractmethod
    def get_tea_masters_by_gender(self, gender: str) -> List[Dict[str, Any]]:
        """根据性别获取茶艺师"""
        pass


class BaseScheduleRepository(ABC):
    """
    茶艺师排班数据访问抽象接口

    定义排班相关的所有数据操作方法
    """

    @abstractmethod
    def add_schedule(self, tea_master_id: int, start_time: datetime, end_time: datetime,
                    status: str, appointment_id: Optional[int] = None) -> int:
        """添加排班"""
        pass

    @abstractmethod
    def get_tea_master_schedules(self, tea_master_id: int, date: datetime) -> List[Dict[str, Any]]:
        """获取茶艺师指定日期的排班"""
        pass

    @abstractmethod
    def is_tea_master_available(self, tea_master_id: int, start_time: datetime, end_time: datetime) -> bool:
        """检查茶艺师时间段是否可用"""
        pass

    @abstractmethod
    def update_schedule_status(self, schedule_id: int, status: str, appointment_id: Optional[int] = None) -> bool:
        """更新排班状态"""
        pass

    @abstractmethod
    def delete_schedule(self, schedule_id: int) -> bool:
        """删除排班"""
        pass


class BaseTeaRoomRepository(ABC):
    """
    茶室/包间数据访问抽象接口

    定义茶室相关的所有数据操作方法
    """

    @abstractmethod
    def add_room(self, name: str, room_type: Optional[str] = None, capacity: Optional[int] = None,
               equipment: Optional[List[str]] = None) -> int:
        """添加茶室"""
        pass

    @abstractmethod
    def get_room_by_id(self, room_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取茶室信息"""
        pass

    @abstractmethod
    def get_all_rooms(self) -> List[Dict[str, Any]]:
        """获取所有茶室"""
        pass

    @abstractmethod
    def update_room(self, room_id: int, **updates) -> bool:
        """更新茶室信息"""
        pass

    @abstractmethod
    def delete_room(self, room_id: int) -> bool:
        """删除茶室"""
        pass

    @abstractmethod
    def get_rooms_by_type(self, room_type: str) -> List[Dict[str, Any]]:
        """根据类型获取茶室"""
        pass


class BaseRoomScheduleRepository(ABC):
    """
    茶室排班数据访问抽象接口

    定义茶室占用/排班相关的所有数据操作方法
    """

    @abstractmethod
    def add_room_schedule(self, room_id: int, start_time: datetime, end_time: datetime,
                         status: str, appointment_id: Optional[int] = None) -> int:
        """添加茶室排班"""
        pass

    @abstractmethod
    def get_room_schedules(self, room_id: int, date: datetime) -> List[Dict[str, Any]]:
        """获取茶室指定日期的排班"""
        pass

    @abstractmethod
    def is_room_available(self, room_id: int, start_time: datetime, end_time: datetime) -> bool:
        """检查茶室时间段是否可用"""
        pass

    @abstractmethod
    def update_room_schedule_status(self, schedule_id: int, status: str, appointment_id: Optional[int] = None) -> bool:
        """更新茶室排班状态"""
        pass

    @abstractmethod
    def delete_room_schedule(self, schedule_id: int) -> bool:
        """删除茶室排班"""
        pass


class BaseInventoryRepository(ABC):
    """
    茶叶库存数据访问抽象接口

    定义库存相关的所有数据操作方法
    """

    @abstractmethod
    def add_item(self, name: str, category: Optional[str] = None, unit: Optional[str] = None,
               stock_quantity: float = 0, reorder_threshold: float = 0,
               unit_price: Optional[float] = None) -> int:
        """添加库存项"""
        pass

    @abstractmethod
    def get_item_by_id(self, item_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取库存项"""
        pass

    @abstractmethod
    def get_all_items(self) -> List[Dict[str, Any]]:
        """获取所有库存项"""
        pass

    @abstractmethod
    def update_item(self, item_id: int, **updates) -> bool:
        """更新库存项信息"""
        pass

    @abstractmethod
    def delete_item(self, item_id: int) -> bool:
        """删除库存项"""
        pass

    @abstractmethod
    def adjust_stock(self, item_id: int, delta: float) -> bool:
        """调整库存数量（增加为正，减少为负）"""
        pass

    @abstractmethod
    def get_low_stock_items(self) -> List[Dict[str, Any]]:
        """获取库存低于补货阈值的项目"""
        pass


class BaseKnowledgeRepository(ABC):
    """
    知识库数据访问抽象接口

    定义知识库相关的所有数据操作方法
    """

    @abstractmethod
    def add_document(self, content: str, category: str, keywords: Optional[List[str]] = None,
                    embedding: Optional[List[float]] = None) -> int:
        """添加知识文档"""
        pass

    @abstractmethod
    def get_document(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """获取指定文档"""
        pass

    @abstractmethod
    def get_all_documents(self, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """获取所有文档"""
        pass

    @abstractmethod
    def update_document(self, doc_id: int, content: Optional[str] = None, category: Optional[str] = None,
                       keywords: Optional[List[str]] = None, embedding: Optional[List[float]] = None) -> bool:
        """更新文档"""
        pass

    @abstractmethod
    def delete_document(self, doc_id: int, soft_delete: bool = True) -> bool:
        """删除文档（支持软删除）"""
        pass

    @abstractmethod
    def search_documents_by_category(self, category: str) -> List[Dict[str, Any]]:
        """按分类搜索文档"""
        pass

    @abstractmethod
    def search_documents_by_keywords(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """按关键词搜索文档"""
        pass

    @abstractmethod
    def get_all_categories(self) -> List[str]:
        """获取所有分类"""
        pass

    @abstractmethod
    def get_documents_count(self) -> int:
        """获取文档总数"""
        pass


class BaseUserBehaviorRepository(ABC):
    """
    用户行为数据访问抽象接口

    定义用户行为分析相关的所有数据操作方法
    """

    @abstractmethod
    def record_behavior(self, user_id: str, action_type: str, action_data: Optional[Dict[str, Any]] = None,
                       tea_master_id: Optional[int] = None, session_id: Optional[str] = None) -> int:
        """记录用户行为"""
        pass

    @abstractmethod
    def get_user_behaviors(self, user_id: str, action_type: Optional[str] = None,
                          days_back: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取用户行为历史"""
        pass

    @abstractmethod
    def update_user_preference(self, user_id: str, preference_type: str, preference_value: str) -> bool:
        """更新用户偏好"""
        pass

    @abstractmethod
    def get_user_preferences(self, user_id: str, preference_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取用户偏好"""
        pass

    @abstractmethod
    def create_recommendation(self, user_id: str, recommendation_type: str, content: str,
                            tea_master_id: Optional[int] = None) -> int:
        """创建推荐"""
        pass

    @abstractmethod
    def get_pending_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """获取待发送的推荐"""
        pass

    @abstractmethod
    def mark_recommendation_sent(self, recommendation_id: int) -> bool:
        """标记推荐为已发送"""
        pass

    @abstractmethod
    def get_user_statistics(self, user_id: str, days_back: int = 30) -> Dict[str, Any]:
        """获取用户统计信息"""
        pass
