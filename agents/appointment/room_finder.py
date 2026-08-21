"""
茶室查找器

负责在预约时间段内为用户查找一个可用的茶室/包间
"""

from typing import Optional, Dict, Any, Callable, List
from datetime import datetime


class TeaRoomFinder:
    """茶室查找器"""

    def __init__(self):
        pass

    def _parse_guest_count(self, guest_count) -> Optional[int]:
        """将预约人数解析为正整数，解析失败或未提供时返回 None"""
        if guest_count is None:
            return None
        if isinstance(guest_count, (int, float)):
            value = int(guest_count)
            return value if value > 0 else None
        digits = ''.join(filter(str.isdigit, str(guest_count)))
        if not digits:
            return None
        value = int(digits)
        return value if value > 0 else None

    def find_available_room(self, start_time: datetime, end_time: datetime,
                          project: str = None, guest_count=None,
                          yield_func: Optional[Callable] = None) -> Optional[Dict[str, Any]]:
        """
        在指定时间段内查找一个可用的茶室

        排序优先级：
        1. 人数（硬约束优先）：优先选容量刚好够坐的茶室，避免把大包间浪费给两三个人；
           如果没有任何茶室能坐下这么多人，则退而求其次，从容量最大的茶室开始尝试。
        2. 服务项目对应的房型偏好（如茶道体验优先安排茶道体验室）。
        3. 可用性：按上述顺序依次检查排班冲突，找到第一个空闲的即可。
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

        guests = self._parse_guest_count(guest_count)
        candidates: List[Dict[str, Any]] = all_rooms

        if guests:
            sufficient = [r for r in all_rooms if (r.get("capacity") or 0) >= guests]
            if sufficient:
                # 容量从小到大：优先选刚好够坐的茶室，减少大包间被小规模预约占用
                sufficient.sort(key=lambda r: r.get("capacity") or 0)
                candidates = sufficient
                if yield_func:
                    yield_func(f"[THOUGHT][预约机器人] 根据{guests}位客人筛选出{len(candidates)}间容量足够的茶室\n")
            else:
                # 没有任何茶室坐得下，退而求其次选容量最大的
                candidates = sorted(all_rooms, key=lambda r: -(r.get("capacity") or 0))
                if yield_func:
                    yield_func(f"[THOUGHT][预约机器人] 没有单间茶室能容纳{guests}位客人，将尝试容量最大的茶室\n")

        # 根据服务项目粗略匹配房型偏好（在人数筛选结果内部再排序）
        preferred_type = None
        if project:
            if "茶道" in project or "仪式" in project or "体验" in project:
                preferred_type = "茶道体验室"

        if preferred_type:
            preferred = [r for r in candidates if r.get("room_type") == preferred_type]
            others = [r for r in candidates if r.get("room_type") != preferred_type]
            candidates = preferred + others

        for room in candidates:
            if room_service.is_room_available(room["id"], start_time, end_time):
                if yield_func:
                    yield_func(f"[THOUGHT][预约机器人] 找到可用茶室：{room['name']}（{room.get('room_type', '')}，容量{room.get('capacity', '?')}人）\n")
                return room

        if yield_func:
            yield_func("[THOUGHT][预约机器人] 该时间段所有符合条件的茶室均已被占用\n")
        return None
