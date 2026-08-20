"""
茶室查找器

负责在预约时间段内为用户查找一个可用的茶室/包间
"""

from typing import Optional, Dict, Any, Callable
from datetime import datetime


class TeaRoomFinder:
    """茶室查找器"""

    def __init__(self):
        pass

    def find_available_room(self, start_time: datetime, end_time: datetime,
                          project: str = None, yield_func: Optional[Callable] = None) -> Optional[Dict[str, Any]]:
        """
        在指定时间段内查找一个可用的茶室

        会优先根据服务项目匹配合适的房型（如茶道体验优先安排茶道体验室），
        找不到匹配房型时再从其余茶室中按可用性挑选。
        """
        from services.tea_room_service import TeaRoomService
        room_service = TeaRoomService()
        room_service.initialize_default_rooms()

        all_rooms = room_service.get_all_rooms()
        if not all_rooms:
            if yield_func:
                yield_func("[THOUGHT][预约机器人] 没有找到任何茶室数据\n")
            return None

        if yield_func:
            yield_func("[THOUGHT][预约机器人] 正在为本次预约挑选合适的茶室...\n")

        # 根据服务项目粗略匹配房型偏好
        preferred_type = None
        if project:
            if "茶道" in project or "仪式" in project or "体验" in project:
                preferred_type = "茶道体验室"

        ordered_rooms = all_rooms
        if preferred_type:
            preferred = [r for r in all_rooms if r.get("room_type") == preferred_type]
            others = [r for r in all_rooms if r.get("room_type") != preferred_type]
            ordered_rooms = preferred + others

        for room in ordered_rooms:
            if room_service.is_room_available(room["id"], start_time, end_time):
                if yield_func:
                    yield_func(f"[THOUGHT][预约机器人] 找到可用茶室：{room['name']}（{room.get('room_type', '')}）\n")
                return room

        if yield_func:
            yield_func("[THOUGHT][预约机器人] 该时间段所有茶室均已被占用\n")
        return None
