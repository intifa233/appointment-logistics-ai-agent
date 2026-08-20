# services/tea_room_service.py

from typing import List, Dict, Any, Optional
from db.db_router import DatabaseRouter
import logging

logger = logging.getLogger(__name__)

class TeaRoomService:
    """茶室服务类 - 管理茶室/包间数据和默认初始化"""

    def __init__(self):
        self.db = DatabaseRouter()

        # 默认茶室数据（4间雅座、3间包间、1间茶道体验室）
        self.default_rooms = [
            {"name": "雅座A", "room_type": "雅座", "capacity": 2, "equipment": ["茶具", "煮水壶"]},
            {"name": "雅座B", "room_type": "雅座", "capacity": 2, "equipment": ["茶具", "煮水壶"]},
            {"name": "雅座C", "room_type": "雅座", "capacity": 4, "equipment": ["茶具", "煮水壶", "香炉"]},
            {"name": "雅座D", "room_type": "雅座", "capacity": 4, "equipment": ["茶具", "煮水壶", "香炉"]},
            {"name": "听雨包间", "room_type": "包间", "capacity": 6, "equipment": ["茶具", "煮水壶", "香炉", "投影"]},
            {"name": "松风包间", "room_type": "包间", "capacity": 6, "equipment": ["茶具", "煮水壶", "香炉"]},
            {"name": "望月包间", "room_type": "包间", "capacity": 8, "equipment": ["茶具", "煮水壶", "香炉", "古筝"]},
            {"name": "禅茶体验室", "room_type": "茶道体验室", "capacity": 10, "equipment": ["茶道全套茶具", "蒲团", "香炉", "投影"]}
        ]

    def initialize_default_rooms(self) -> bool:
        """初始化默认茶室数据"""
        try:
            existing_rooms = self.db.tea_rooms.get_all_rooms()

            if existing_rooms:
                logger.info(f"数据库中已有 {len(existing_rooms)} 间茶室，跳过初始化")
                return True

            logger.info("数据库中无茶室数据，开始初始化默认茶室")

            for room_data in self.default_rooms:
                try:
                    room_id = self.db.tea_rooms.add_room(
                        name=room_data['name'],
                        room_type=room_data['room_type'],
                        capacity=room_data['capacity'],
                        equipment=room_data['equipment']
                    )
                    logger.debug(f"添加茶室: {room_data['name']} (ID: {room_id})")

                except Exception as e:
                    logger.error(f"添加茶室 {room_data['name']} 失败: {e}")
                    return False

            final_count = len(self.db.tea_rooms.get_all_rooms())
            logger.info(f"茶室初始化完成，共添加 {final_count} 间茶室")
            return True

        except Exception as e:
            logger.error(f"茶室初始化失败: {e}")
            return False

    def get_all_rooms(self) -> List[Dict[str, Any]]:
        """获取所有茶室信息"""
        return self.db.tea_rooms.get_all_rooms()

    def get_room_by_id(self, room_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取茶室信息"""
        return self.db.tea_rooms.get_room_by_id(room_id)

    def get_rooms_by_type(self, room_type: str) -> List[Dict[str, Any]]:
        """根据类型获取茶室"""
        return self.db.tea_rooms.get_rooms_by_type(room_type)

    def get_room_schedules(self, room_id: int, date) -> List[Dict[str, Any]]:
        """获取茶室指定日期的排班信息"""
        return self.db.tea_rooms.get_room_schedules(room_id, date)

    def is_room_available(self, room_id: int, start_time, end_time) -> bool:
        """检查茶室在指定时间段是否可用"""
        return self.db.tea_rooms.is_room_available(room_id, start_time, end_time)

    def reserve_room(self, room_id: int, start_time, end_time, appointment_id: int = None) -> int:
        """预约茶室（占用其排班时段）"""
        return self.db.tea_rooms.add_room_schedule(
            room_id=room_id,
            start_time=start_time,
            end_time=end_time,
            status="busy",
            appointment_id=appointment_id
        )

    def add_room(self, name: str, room_type: str = None, capacity: int = None,
               equipment: List[str] = None) -> int:
        """添加新茶室"""
        return self.db.tea_rooms.add_room(name, room_type, capacity, equipment)

    def get_rooms_count(self) -> int:
        """获取茶室总数"""
        return len(self.db.tea_rooms.get_all_rooms())
