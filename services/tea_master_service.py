# services/tea_master_service.py

from typing import List, Dict, Any
from db.db_router import DatabaseRouter
import logging

logger = logging.getLogger(__name__)

class TeaMasterService:
    """茶艺师服务类 - 管理茶艺师数据和默认初始化"""

    def __init__(self):
        self.db = DatabaseRouter()

        # 默认茶艺师数据（10人，专长覆盖不同茶艺方向）
        self.default_tea_masters = [
            {
                "name": "张伟",
                "gender": "男",
                "specialty": "精通功夫茶艺，注重冲泡节奏与仪态，擅长为客人细致讲解茶具与冲泡步骤"
            },
            {
                "name": "王强",
                "gender": "男",
                "specialty": "功夫茶艺专家，手法娴熟，专注于乌龙茶系的多次冲泡与回甘变化讲解"
            },
            {
                "name": "李娜",
                "gender": "女",
                "specialty": "茶艺讲解细腻温和，擅长花茶調配，适合初次品茶、想放松心情的客人"
            },
            {
                "name": "赵敏",
                "gender": "女",
                "specialty": "精通普洱鉴赏与陈化知识，善于根据客人口味推荐生普或熟普"
            },
            {
                "name": "刘洋",
                "gender": "男",
                "specialty": "潮汕工夫茶高手，泡法讲究，适合喜欢仪式感和茶文化交流的客户"
            },
            {
                "name": "孙丽",
                "gender": "女",
                "specialty": "日式抹茶道造诣深厚，动作优雅，适合喜欢静心体验茶道仪式的客户"
            },
            {
                "name": "周杰",
                "gender": "男",
                "specialty": "白茶收藏与冲泡经验丰富，擅长为客人讲解不同年份白茶的风味变化"
            },
            {
                "name": "吴婷",
                "gender": "女",
                "specialty": "茶席设计与美学专家，擅长根据包间氛围搭配茶席，视觉与品饮体验俱佳"
            },
            {
                "name": "郑斌",
                "gender": "男",
                "specialty": "新式茶饮调配达人，也懂传统茶艺，适合喜欢尝试创新茶饮的年轻客户"
            },
            {
                "name": "何静",
                "gender": "女",
                "specialty": "茶叶审评与禅茶文化讲解，适合希望深入了解茶文化、追求静心体验的客户"
            }
        ]

    def initialize_default_tea_masters(self) -> bool:
        """初始化默认茶艺师数据"""
        try:
            # 检查是否已有茶艺师数据
            existing_tea_masters = self.db.tea_masters.get_all_tea_masters()

            if existing_tea_masters:
                logger.info(f"数据库中已有 {len(existing_tea_masters)} 位茶艺师，跳过初始化")
                return True

            logger.info("数据库中无茶艺师数据，开始初始化默认茶艺师")

            # 添加默认茶艺师
            for tm_data in self.default_tea_masters:
                try:
                    tm_id = self.db.tea_masters.add_tea_master(
                        name=tm_data['name'],
                        gender=tm_data['gender'],
                        specialty=tm_data['specialty']
                    )
                    logger.debug(f"添加茶艺师: {tm_data['name']} (ID: {tm_id})")

                except Exception as e:
                    logger.error(f"添加茶艺师 {tm_data['name']} 失败: {e}")
                    return False

            # 验证初始化结果
            final_count = len(self.db.tea_masters.get_all_tea_masters())
            logger.info(f"茶艺师初始化完成，共添加 {final_count} 位茶艺师")
            return True

        except Exception as e:
            logger.error(f"茶艺师初始化失败: {e}")
            return False

    def get_all_tea_masters(self) -> List[Dict[str, Any]]:
        """获取所有茶艺师信息"""
        return self.db.tea_masters.get_all_tea_masters()

    def get_tea_master_by_name(self, name: str) -> Dict[str, Any]:
        """根据姓名获取茶艺师信息"""
        return self.db.tea_masters.get_tea_master_by_name(name)

    def get_tea_master_by_id(self, tea_master_id: int) -> Dict[str, Any]:
        """根据ID获取茶艺师信息"""
        return self.db.tea_masters.get_tea_master_by_id(tea_master_id)

    def get_tea_master_schedules(self, tea_master_id: int, date) -> List[Dict[str, Any]]:
        """获取茶艺师指定日期的排班信息"""
        return self.db.tea_masters.get_tea_master_schedules(tea_master_id, date)

    def is_tea_master_available(self, tea_master_id: int, start_time, end_time) -> bool:
        """检查茶艺师在指定时间段是否可用"""
        return self.db.tea_masters.is_tea_master_available(tea_master_id, start_time, end_time)

    def add_tea_master(self, name: str, gender: str = None, specialty: str = None) -> int:
        """添加新茶艺师"""
        return self.db.tea_masters.add_tea_master(name, gender, specialty)

    def get_tea_masters_count(self) -> int:
        """获取茶艺师总数"""
        tea_masters = self.db.tea_masters.get_all_tea_masters()
        return len(tea_masters)
