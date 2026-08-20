"""
预约服务层

职责：
1. 封装预约相关的数据库操作
2. 处理预约业务逻辑
3. 提供预约相关的数据服务
"""

import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from db.db_router import DatabaseRouter
import logging

logger = logging.getLogger(__name__)

class AppointmentService:
    """预约服务类"""

    def __init__(self, db_path: str = 'sqlite:///data/tea_house.db'):
        self.db_router = DatabaseRouter(db_path)
        self.tea_master_repo = self.db_router.tea_masters

    def save_appointment(self, tea_master_id: Optional[str], start_time: datetime,
                        end_time: datetime, appointment_history: Dict[str, Any],
                        session_id: str) -> bool:
        """保存预约信息到数据库

        tea_master_id 为 None 时表示本次预约不需要专属茶艺师，
        此时不会创建茶艺师排班占用记录，仅保留预约时间信息用于用户行为记录。
        """
        try:
            appointment_id = int(time.time() * 1000)

            # 只有指定了茶艺师才需要占用其排班
            if tea_master_id is not None:
                self.tea_master_repo.add_schedule(
                    tea_master_id=int(tea_master_id),
                    start_time=start_time,
                    end_time=end_time,
                    status="busy",
                    appointment_id=appointment_id
                )

            logger.info(f"预约信息已保存到数据库：茶艺师ID={tea_master_id or '无'}, 时间={start_time} 到 {end_time}, 预约ID={appointment_id}")
            return True

        except Exception as e:
            logger.error(f"保存预约信息到数据库失败：{e}")
            return False

    def get_tea_master_by_id(self, tea_master_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取茶艺师信息"""
        try:
            return self.tea_master_repo.get_tea_master_by_id(tea_master_id)
        except Exception as e:
            logger.error(f"获取茶艺师信息失败：{e}")
            return None

    def get_tea_master_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据姓名获取茶艺师信息"""
        try:
            return self.tea_master_repo.get_tea_master_by_name(name)
        except Exception as e:
            logger.error(f"获取茶艺师信息失败：{e}")
            return None

    def get_all_tea_masters(self) -> List[Dict[str, Any]]:
        """获取所有茶艺师信息"""
        try:
            return self.tea_master_repo.get_all_tea_masters()
        except Exception as e:
            logger.error(f"获取茶艺师列表失败：{e}")
            return []

    def get_tea_masters_by_gender(self, gender: str) -> List[Dict[str, Any]]:
        """根据性别获取茶艺师信息"""
        try:
            return self.tea_master_repo.get_tea_masters_by_gender(gender)
        except Exception as e:
            logger.error(f"根据性别获取茶艺师信息失败：{e}")
            return []

    def get_tea_master_schedules(self, tea_master_id: int, date) -> List[Dict[str, Any]]:
        """获取茶艺师排班信息"""
        try:
            return self.tea_master_repo.get_tea_master_schedules(tea_master_id, date)
        except Exception as e:
            logger.error(f"获取茶艺师排班信息失败：{e}")
            return []

    def is_tea_master_available(self, tea_master_id: int, start_time: datetime, end_time: datetime) -> bool:
        """检查茶艺师是否可用"""
        try:
            return self.tea_master_repo.is_tea_master_available(tea_master_id, start_time, end_time)
        except Exception as e:
            logger.error(f"检查茶艺师可用性失败：{e}")
            return False

    def add_tea_master(self, name: str, gender: str = None, specialty: str = None) -> Optional[int]:
        """添加新茶艺师"""
        try:
            return self.tea_master_repo.add_tea_master(name, gender, specialty)
        except Exception as e:
            logger.error(f"添加茶艺师失败：{e}")
            return None

    def get_all_specialties(self) -> List[str]:
        """获取所有茶艺师的专长列表"""
        try:
            return self.tea_master_repo.get_all_specialties()
        except Exception as e:
            logger.error(f"获取茶艺师专长列表失败：{e}")
            return []
