"""
预约数据库操作器

负责处理预约相关的数据库操作
注意：现在通过Services层访问数据库，符合分层架构
"""

import time
from typing import Dict, Any, Optional
from datetime import datetime
from config.time_config import time_config
from config.constants import tea_master_busy_periods_dict, room_busy_periods_dict


class AppointmentDatabase:
    """预约数据库操作器"""

    def __init__(self):
        # 延迟导入Services避免循环依赖
        self._appointment_service = None
        self._user_behavior_service = None
        self._tea_room_service = None

    @property
    def appointment_service(self):
        """懒加载预约服务"""
        if self._appointment_service is None:
            from services.appointment_service import AppointmentService
            self._appointment_service = AppointmentService()
        return self._appointment_service

    @property
    def user_behavior_service(self):
        """懒加载用户行为服务"""
        if self._user_behavior_service is None:
            from services.user_behavior_service import UserBehaviorService
            self._user_behavior_service = UserBehaviorService()
        return self._user_behavior_service

    @property
    def tea_room_service(self):
        """懒加载茶室服务"""
        if self._tea_room_service is None:
            from services.tea_room_service import TeaRoomService
            self._tea_room_service = TeaRoomService()
        return self._tea_room_service

    def save_appointment(self, tea_master_id: Optional[str], start_time: datetime,
                        end_time: datetime, appointment_history: Dict[str, Any],
                        session_id: str) -> bool:
        """保存预约信息到数据库（tea_master_id 为 None 表示不需要专属茶艺师）"""
        try:
            # 通过Services层保存预约
            success = self.appointment_service.save_appointment(
                tea_master_id, start_time, end_time, appointment_history, session_id
            )

            if success:
                # 记录用户行为
                self._record_user_behavior(start_time, end_time, tea_master_id,
                                         appointment_history, session_id)

            return success

        except Exception as e:
            print(f"保存预约信息到数据库失败：{e}")
            return False

    def update_memory_schedule(self, tea_master_id: str, start_time: datetime, end_time: datetime):
        """更新内存中的茶艺师忙碌时间段"""
        busy_period = {
            "start": time_config.format_datetime(start_time, "%H:%M"),
            "end": time_config.format_datetime(end_time, "%H:%M")
        }
        tea_master_busy_periods_dict.setdefault(tea_master_id, []).append(busy_period)

    def save_room_reservation(self, room_id: int, start_time: datetime, end_time: datetime) -> bool:
        """预约茶室（占用其排班时段）"""
        try:
            appointment_id = int(time.time() * 1000)
            self.tea_room_service.reserve_room(room_id, start_time, end_time, appointment_id)
            self.update_memory_room_schedule(room_id, start_time, end_time)
            return True
        except Exception as e:
            print(f"预约茶室失败：{e}")
            return False

    def update_memory_room_schedule(self, room_id: int, start_time: datetime, end_time: datetime):
        """更新内存中的茶室占用时间段"""
        busy_period = {
            "start": time_config.format_datetime(start_time, "%H:%M"),
            "end": time_config.format_datetime(end_time, "%H:%M")
        }
        room_busy_periods_dict.setdefault(room_id, []).append(busy_period)

    def _record_user_behavior(self, start_time: datetime, end_time: datetime,
                            tea_master_id: Optional[str], appointment_history: Dict[str, Any],
                            session_id: str):
        """记录用户预约行为"""
        try:
            action_data = {
                'start_time': time_config.format_datetime(start_time, "%Y-%m-%d %H:%M:%S"),
                'end_time': time_config.format_datetime(end_time, "%Y-%m-%d %H:%M:%S"),
                'duration': int((end_time - start_time).total_seconds() / 60),
                'project': appointment_history.get('project', 'tea_service'),
                'preference': appointment_history.get('preference', ''),
                'tea_master_id': tea_master_id
            }

            # 通过Services层记录用户行为
            self.user_behavior_service.record_behavior(
                user_id="default_user",  # 统一使用default_user作为用户ID
                action_type='appointment',
                action_data=action_data,
                tea_master_id=str(tea_master_id) if tea_master_id is not None else None,
                session_id=session_id
            )

        except Exception as behavior_error:
            print(f"记录用户行为失败（但预约仍然成功）：{behavior_error}")
