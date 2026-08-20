from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ..base.interfaces import BaseTeaMasterRepository, BaseScheduleRepository
from ..base.session_manager import SessionManager
from ..models import TeaMaster, TeaMasterSchedule


class TeaMasterRepository(BaseTeaMasterRepository, BaseScheduleRepository):
    """
    茶艺师数据访问对象

    职责：
    1. 茶艺师信息的CRUD操作
    2. 茶艺师排班的管理
    3. 茶艺师可用性检查
    """

    def __init__(self, session_manager: SessionManager):
        """
        初始化茶艺师数据仓库

        Args:
            session_manager: 会话管理器
        """
        self.session_manager = session_manager

    def add_tea_master(self, name: str, gender: Optional[str] = None, specialty: Optional[str] = None) -> int:
        """
        添加新茶艺师

        Args:
            name: 茶艺师姓名
            gender: 性别
            specialty: 专长

        Returns:
            新创建的茶艺师ID
        """
        with self.session_manager.session_scope() as session:
            tea_master = TeaMaster(name=name, gender=gender, specialty=specialty)
            session.add(tea_master)
            session.flush()
            return tea_master.id

    def get_tea_master_by_id(self, tea_master_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取茶艺师信息

        Args:
            tea_master_id: 茶艺师ID

        Returns:
            茶艺师信息字典，如果不存在返回None
        """
        with self.session_manager.session_scope() as session:
            tea_master = session.query(TeaMaster).filter(
                TeaMaster.id == tea_master_id
            ).first()

            if not tea_master:
                return None

            return self._tea_master_to_dict(tea_master)

    def get_tea_master_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        根据姓名获取茶艺师信息

        Args:
            name: 茶艺师姓名

        Returns:
            茶艺师信息字典，如果不存在返回None
        """
        with self.session_manager.session_scope() as session:
            tea_master = session.query(TeaMaster).filter(
                TeaMaster.name == name
            ).first()

            if not tea_master:
                return None

            return self._tea_master_to_dict(tea_master)

    def get_all_tea_masters(self) -> List[Dict[str, Any]]:
        """
        获取所有茶艺师信息

        Returns:
            茶艺师信息列表
        """
        with self.session_manager.session_scope() as session:
            tea_masters = session.query(TeaMaster).all()
            return [self._tea_master_to_dict(tm) for tm in tea_masters]

    def get_all_specialties(self) -> List[str]:
        """
        获取所有茶艺师的专长列表

        Returns:
            专长列表（去重后）
        """
        with self.session_manager.session_scope() as session:
            specialties = session.query(TeaMaster.specialty).distinct().all()
            return [s[0] for s in specialties if s[0] is not None]

    def update_tea_master(self, tea_master_id: int, **updates) -> bool:
        """
        更新茶艺师信息

        Args:
            tea_master_id: 茶艺师ID
            **updates: 要更新的字段

        Returns:
            更新是否成功
        """
        with self.session_manager.session_scope() as session:
            tea_master = session.query(TeaMaster).filter(
                TeaMaster.id == tea_master_id
            ).first()

            if not tea_master:
                return False

            for key, value in updates.items():
                if hasattr(tea_master, key):
                    setattr(tea_master, key, value)

            return True

    def delete_tea_master(self, tea_master_id: int) -> bool:
        """
        删除茶艺师

        Args:
            tea_master_id: 茶艺师ID

        Returns:
            删除是否成功
        """
        with self.session_manager.session_scope() as session:
            tea_master = session.query(TeaMaster).filter(
                TeaMaster.id == tea_master_id
            ).first()

            if not tea_master:
                return False

            session.delete(tea_master)
            return True

    # 排班相关方法
    def add_schedule(self, tea_master_id: int, start_time: datetime, end_time: datetime,
                    status: str, appointment_id: Optional[int] = None) -> int:
        """
        添加茶艺师排班

        Args:
            tea_master_id: 茶艺师ID
            start_time: 开始时间
            end_time: 结束时间
            status: 状态 ('busy' 或 'free')
            appointment_id: 预约ID（如果是忙碌状态）

        Returns:
            新创建的排班ID
        """
        with self.session_manager.session_scope() as session:
            schedule = TeaMasterSchedule(
                tea_master_id=tea_master_id,
                start_time=start_time,
                end_time=end_time,
                status=status,
                appointment_id=appointment_id
            )
            session.add(schedule)
            session.flush()
            return schedule.id

    def get_tea_master_schedules(self, tea_master_id: int, date: datetime) -> List[Dict[str, Any]]:
        """
        获取茶艺师指定日期的排班

        Args:
            tea_master_id: 茶艺师ID
            date: 查询日期

        Returns:
            排班信息列表
        """
        with self.session_manager.session_scope() as session:
            start = datetime(date.year, date.month, date.day)
            end = start + timedelta(days=1)

            schedules = session.query(TeaMasterSchedule).filter(
                TeaMasterSchedule.tea_master_id == tea_master_id,
                TeaMasterSchedule.start_time >= start,
                TeaMasterSchedule.end_time < end
            ).all()

            return [self._schedule_to_dict(schedule) for schedule in schedules]

    def is_tea_master_available(self, tea_master_id: int, start_time: datetime, end_time: datetime) -> bool:
        """
        检查茶艺师在指定时间段是否可用

        Args:
            tea_master_id: 茶艺师ID
            start_time: 开始时间
            end_time: 结束时间

        Returns:
            是否可用
        """
        with self.session_manager.session_scope() as session:
            conflict = session.query(TeaMasterSchedule).filter(
                TeaMasterSchedule.tea_master_id == tea_master_id,
                TeaMasterSchedule.status == "busy",
                TeaMasterSchedule.start_time < end_time,
                TeaMasterSchedule.end_time > start_time
            ).first()

            return conflict is None

    def update_schedule_status(self, schedule_id: int, status: str, appointment_id: Optional[int] = None) -> bool:
        """
        更新排班状态

        Args:
            schedule_id: 排班ID
            status: 新状态
            appointment_id: 预约ID

        Returns:
            更新是否成功
        """
        with self.session_manager.session_scope() as session:
            schedule = session.query(TeaMasterSchedule).filter(
                TeaMasterSchedule.id == schedule_id
            ).first()

            if not schedule:
                return False

            schedule.status = status
            if appointment_id is not None:
                schedule.appointment_id = appointment_id

            return True

    def delete_schedule(self, schedule_id: int) -> bool:
        """
        删除排班

        Args:
            schedule_id: 排班ID

        Returns:
            删除是否成功
        """
        with self.session_manager.session_scope() as session:
            schedule = session.query(TeaMasterSchedule).filter(
                TeaMasterSchedule.id == schedule_id
            ).first()

            if not schedule:
                return False

            session.delete(schedule)
            return True

    def get_tea_masters_by_gender(self, gender: str) -> List[Dict[str, Any]]:
        """
        根据性别获取茶艺师信息

        Args:
            gender: 茶艺师性别

        Returns:
            茶艺师信息列表
        """
        with self.session_manager.session_scope() as session:
            tea_masters = session.query(TeaMaster).filter(
                TeaMaster.gender == gender
            ).all()
            return [self._tea_master_to_dict(tm) for tm in tea_masters]

    def _tea_master_to_dict(self, tea_master: TeaMaster) -> Dict[str, Any]:
        """将茶艺师对象转换为字典"""
        return {
            'id': tea_master.id,
            'name': tea_master.name,
            'gender': tea_master.gender,
            'specialty': tea_master.specialty
        }

    def _schedule_to_dict(self, schedule: TeaMasterSchedule) -> Dict[str, Any]:
        """将排班对象转换为字典"""
        return {
            'id': schedule.id,
            'tea_master_id': schedule.tea_master_id,
            'start_time': schedule.start_time,
            'end_time': schedule.end_time,
            'status': schedule.status,
            'appointment_id': schedule.appointment_id
        }
