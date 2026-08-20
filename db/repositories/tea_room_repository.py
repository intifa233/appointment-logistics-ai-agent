from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ..base.interfaces import BaseTeaRoomRepository, BaseRoomScheduleRepository
from ..base.session_manager import SessionManager
from ..models import TeaRoom, TeaRoomSchedule


class TeaRoomRepository(BaseTeaRoomRepository, BaseRoomScheduleRepository):
    """
    茶室数据访问对象

    职责：
    1. 茶室/包间信息的CRUD操作
    2. 茶室占用排班的管理
    3. 茶室可用性检查
    """

    def __init__(self, session_manager: SessionManager):
        """
        初始化茶室数据仓库

        Args:
            session_manager: 会话管理器
        """
        self.session_manager = session_manager

    def add_room(self, name: str, room_type: Optional[str] = None, capacity: Optional[int] = None,
               equipment: Optional[List[str]] = None) -> int:
        """
        添加茶室

        Args:
            name: 茶室名称
            room_type: 类型（雅座/包间/茶道体验室）
            capacity: 可容纳人数
            equipment: 设备清单

        Returns:
            新创建的茶室ID
        """
        with self.session_manager.session_scope() as session:
            room = TeaRoom(name=name, room_type=room_type, capacity=capacity, equipment=equipment)
            session.add(room)
            session.flush()
            return room.id

    def get_room_by_id(self, room_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取茶室信息"""
        with self.session_manager.session_scope() as session:
            room = session.query(TeaRoom).filter(TeaRoom.id == room_id).first()
            if not room:
                return None
            return self._room_to_dict(room)

    def get_all_rooms(self) -> List[Dict[str, Any]]:
        """获取所有茶室"""
        with self.session_manager.session_scope() as session:
            rooms = session.query(TeaRoom).all()
            return [self._room_to_dict(room) for room in rooms]

    def update_room(self, room_id: int, **updates) -> bool:
        """更新茶室信息"""
        with self.session_manager.session_scope() as session:
            room = session.query(TeaRoom).filter(TeaRoom.id == room_id).first()
            if not room:
                return False
            for key, value in updates.items():
                if hasattr(room, key):
                    setattr(room, key, value)
            return True

    def delete_room(self, room_id: int) -> bool:
        """删除茶室"""
        with self.session_manager.session_scope() as session:
            room = session.query(TeaRoom).filter(TeaRoom.id == room_id).first()
            if not room:
                return False
            session.delete(room)
            return True

    def get_rooms_by_type(self, room_type: str) -> List[Dict[str, Any]]:
        """根据类型获取茶室"""
        with self.session_manager.session_scope() as session:
            rooms = session.query(TeaRoom).filter(TeaRoom.room_type == room_type).all()
            return [self._room_to_dict(room) for room in rooms]

    # 排班相关方法
    def add_room_schedule(self, room_id: int, start_time: datetime, end_time: datetime,
                         status: str, appointment_id: Optional[int] = None) -> int:
        """添加茶室排班"""
        with self.session_manager.session_scope() as session:
            schedule = TeaRoomSchedule(
                room_id=room_id,
                start_time=start_time,
                end_time=end_time,
                status=status,
                appointment_id=appointment_id
            )
            session.add(schedule)
            session.flush()
            return schedule.id

    def get_room_schedules(self, room_id: int, date: datetime) -> List[Dict[str, Any]]:
        """获取茶室指定日期的排班"""
        with self.session_manager.session_scope() as session:
            start = datetime(date.year, date.month, date.day)
            end = start + timedelta(days=1)

            schedules = session.query(TeaRoomSchedule).filter(
                TeaRoomSchedule.room_id == room_id,
                TeaRoomSchedule.start_time >= start,
                TeaRoomSchedule.end_time < end
            ).all()

            return [self._schedule_to_dict(schedule) for schedule in schedules]

    def is_room_available(self, room_id: int, start_time: datetime, end_time: datetime) -> bool:
        """检查茶室在指定时间段是否可用"""
        with self.session_manager.session_scope() as session:
            conflict = session.query(TeaRoomSchedule).filter(
                TeaRoomSchedule.room_id == room_id,
                TeaRoomSchedule.status == "busy",
                TeaRoomSchedule.start_time < end_time,
                TeaRoomSchedule.end_time > start_time
            ).first()

            return conflict is None

    def update_room_schedule_status(self, schedule_id: int, status: str, appointment_id: Optional[int] = None) -> bool:
        """更新茶室排班状态"""
        with self.session_manager.session_scope() as session:
            schedule = session.query(TeaRoomSchedule).filter(TeaRoomSchedule.id == schedule_id).first()
            if not schedule:
                return False
            schedule.status = status
            if appointment_id is not None:
                schedule.appointment_id = appointment_id
            return True

    def delete_room_schedule(self, schedule_id: int) -> bool:
        """删除茶室排班"""
        with self.session_manager.session_scope() as session:
            schedule = session.query(TeaRoomSchedule).filter(TeaRoomSchedule.id == schedule_id).first()
            if not schedule:
                return False
            session.delete(schedule)
            return True

    def _room_to_dict(self, room: TeaRoom) -> Dict[str, Any]:
        """将茶室对象转换为字典"""
        return {
            'id': room.id,
            'name': room.name,
            'room_type': room.room_type,
            'capacity': room.capacity,
            'equipment': room.equipment,
            'status': room.status
        }

    def _schedule_to_dict(self, schedule: TeaRoomSchedule) -> Dict[str, Any]:
        """将排班对象转换为字典"""
        return {
            'id': schedule.id,
            'room_id': schedule.room_id,
            'start_time': schedule.start_time,
            'end_time': schedule.end_time,
            'status': schedule.status,
            'appointment_id': schedule.appointment_id
        }
