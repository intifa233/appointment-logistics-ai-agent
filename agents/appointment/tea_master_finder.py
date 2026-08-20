"""
茶艺师查找器

负责根据用户需求查找合适的茶艺师
"""

from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta
from services.text_embedding import find_best_match_indices


class TeaMasterFinder:
    """茶艺师查找器"""

    def __init__(self):
        pass

    def parse_time_and_duration(self, start_time_str: str, duration_str: str) -> tuple:
        """解析预约时间和时长"""
        if not start_time_str or start_time_str == "未知":
            return None, None, None

        if not duration_str or duration_str == "未知":
            return None, None, None

        try:
            from config.time_config import time_config
            start_time = time_config.parse_datetime(start_time_str)
            if start_time is None:
                return None, None, None

            # 从字符串中提取数字作为时长（分钟）
            duration_min = int(''.join(filter(str.isdigit, str(duration_str))))
            if duration_min <= 0:
                return None, None, None

            end_time = start_time + timedelta(minutes=duration_min)
            return start_time, end_time, duration_min
        except Exception:
            return None, None, None

    def find_specific_tea_master(self, tea_master_name: str, start_time: datetime,
                               end_time: datetime, yield_func: Optional[Callable] = None) -> Optional[Dict]:
        """查找指定茶艺师的可用性"""
        # 通过Services层访问数据库
        from services.appointment_service import AppointmentService
        appointment_service = AppointmentService()

        if yield_func:
            yield_func(f"[THOUGHT][预约机器人] 用户指定了茶艺师：{tea_master_name}，正在查询该茶艺师信息...\n")

        specific_tm = appointment_service.get_tea_master_by_name(tea_master_name)
        if specific_tm:
            if yield_func:
                yield_func(f"[THOUGHT][预约机器人] 找到茶艺师：{specific_tm['name']}，正在检查档期...\n")

            if appointment_service.is_tea_master_available(specific_tm["id"], start_time, end_time):
                if yield_func:
                    yield_func(f"[THOUGHT][预约机器人] {tea_master_name}茶艺师在指定时间有空\n")
                return specific_tm
            else:
                if yield_func:
                    yield_func(f"[THOUGHT][预约机器人] {tea_master_name}茶艺师在指定时间不空闲\n")
                return None
        else:
            if yield_func:
                yield_func(f"[THOUGHT][预约机器人] 未找到名为'{tea_master_name}'的茶艺师\n")
            return None

    def find_similar_available_tea_master(self, target_tea_master: Dict[str, Any],
                                        start_time: datetime, end_time: datetime,
                                        yield_func: Optional[Callable] = None) -> Optional[Dict]:
        """根据目标茶艺师的专长查找相似且可用的茶艺师"""
        # 通过Services层访问数据库
        from services.appointment_service import AppointmentService
        appointment_service = AppointmentService()

        if yield_func:
            yield_func(f"[THOUGHT][预约机器人] 正在根据{target_tea_master['name']}的专长查找相似茶艺师...\n")

        # 获取所有茶艺师
        all_tms = appointment_service.get_all_tea_masters()
        if not all_tms:
            return None

        # 排除目标茶艺师本身
        other_tms = [tm for tm in all_tms if tm['id'] != target_tea_master['id']]
        if not other_tms:
            return None

        # 获取目标茶艺师的专长
        target_specialty = target_tea_master.get('specialty', '')
        if not target_specialty:
            return None

        # 使用文本嵌入找到最相似的茶艺师
        specialties = [tm.get('specialty', '') for tm in other_tms]
        indices = find_best_match_indices(target_specialty, specialties)

        if yield_func:
            yield_func(f"[THOUGHT][预约机器人] 根据专长相似度排序，准备检查可用性...\n")

        # 按相似度顺序检查茶艺师可用性
        for index in indices:
            similar_tm = other_tms[index]
            if appointment_service.is_tea_master_available(similar_tm["id"], start_time, end_time):
                if yield_func:
                    yield_func(f"[THOUGHT][预约机器人] 找到相似且可用的茶艺师：{similar_tm['name']}\n")
                return similar_tm

        if yield_func:
            yield_func(f"[THOUGHT][预约机器人] 没有找到相似且可用的茶艺师\n")
        return None

    def filter_tea_masters_by_preference(self, all_tms: list, preference: str) -> list:
        """根据偏好筛选茶艺师"""
        if not preference or preference == "无":
            return all_tms

        specialties = [tm.get("specialty", "") for tm in all_tms]
        indices = find_best_match_indices(preference, specialties)
        return [all_tms[i] for i in indices]

    def filter_tea_masters_by_gender(self, all_tms: list, gender: str) -> list:
        """根据性别筛选茶艺师"""
        if not gender or gender == "未知" or gender == "无":
            return all_tms

        # 标准化性别表示
        gender = gender.strip().lower()
        if gender in ["男", "男性", "男茶艺师", "male"]:
            target_gender = "男"
        elif gender in ["女", "女性", "女茶艺师", "female"]:
            target_gender = "女"
        else:
            return all_tms

        # 筛选匹配性别的茶艺师
        filtered_tms = []
        for tm in all_tms:
            tm_gender = tm.get("gender", "").strip()
            if tm_gender == target_gender:
                filtered_tms.append(tm)

        return filtered_tms if filtered_tms else all_tms  # 如果没有匹配的，返回所有茶艺师

    def find_available_tea_master(self, filtered_tms: list, all_tms: list,
                                start_time: datetime, end_time: datetime,
                                preference: str, gender: str = None, yield_func: Optional[Callable] = None) -> Optional[Dict]:
        """在茶艺师列表中查找可用茶艺师"""
        # 通过Services层访问数据库
        from services.appointment_service import AppointmentService
        appointment_service = AppointmentService()

        if yield_func:
            yield_func("[THOUGHT][预约机器人] 正在查找空闲茶艺师...\n")

        # 先在筛选后的茶艺师中查找
        for tm in filtered_tms:
            if appointment_service.is_tea_master_available(tm["id"], start_time, end_time):
                if yield_func:
                    yield_func(f"[THOUGHT][预约机器人] 找到空闲茶艺师：{tm['name']}\n")
                return tm

        # 如果有偏好但没找到，再在所有茶艺师中查找
        if preference and preference != "无" and filtered_tms != all_tms:
            if yield_func:
                yield_func("[THOUGHT][预约机器人] 偏好茶艺师无空闲，尝试查找所有茶艺师...\n")
            for tm in all_tms:
                if appointment_service.is_tea_master_available(tm["id"], start_time, end_time):
                    if yield_func:
                        yield_func(f"[THOUGHT][预约机器人] 找到空闲茶艺师：{tm['name']}\n")
                    return tm

        if yield_func:
            yield_func("[THOUGHT][预约机器人] 没有找到空闲茶艺师\n")
        return None

    def find_tea_master_with_thought(self, appointment_history: Dict[str, Any],
                                   yield_func: Optional[Callable] = None) -> Optional[Dict]:
        """带思考提示的茶艺师检索流程"""
        # 通过Services层访问数据库
        from services.appointment_service import AppointmentService
        appointment_service = AppointmentService()

        preference = appointment_history.get("preference")
        gender = appointment_history.get("gender")
        start_time_str = appointment_history.get("start_time")
        duration_str = appointment_history.get("duration")
        tea_master_name = appointment_history.get("tea_master_name")

        # 解析时间和时长
        start_time, end_time, duration_min = self.parse_time_and_duration(start_time_str, duration_str)
        if not start_time or not end_time:
            if yield_func:
                yield_func("[THOUGHT][预约机器人] 预约时间或时长信息不完整，无法检索茶艺师\n")
            return None

        if yield_func:
            yield_func("[THOUGHT][预约机器人] 正在解析预约时间和时长...\n")

        # 优先处理指定茶艺师
        if tea_master_name and tea_master_name != "未知":
            specific_tm = self.find_specific_tea_master(tea_master_name, start_time, end_time, yield_func)

            # 如果指定茶艺师可用，直接返回
            if specific_tm:
                return specific_tm

            # 如果指定茶艺师不可用，查找相似茶艺师并返回推荐信息
            target_tm = appointment_service.get_tea_master_by_name(tea_master_name)
            if target_tm:
                similar_tm = self.find_similar_available_tea_master(target_tm, start_time, end_time, yield_func)
                if similar_tm:
                    # 返回包含推荐信息的结果，但标记为需要用户确认
                    return {
                        'is_recommendation': True,
                        'original_tea_master': target_tm,
                        'recommended_tea_master': similar_tm,
                        'requires_confirmation': True
                    }

            # 如果没有找到目标茶艺师或相似茶艺师，返回None
            return None

        # 通用查询逻辑
        if yield_func:
            yield_func("[THOUGHT][预约机器人] 正在检索所有茶艺师数据...\n")

        all_tms = appointment_service.get_all_tea_masters()
        if not all_tms:
            if yield_func:
                yield_func("[THOUGHT][预约机器人] 没有找到任何茶艺师数据\n")
            return None

        # 先根据性别筛选茶艺师
        gender_filtered_tms = self.filter_tea_masters_by_gender(all_tms, gender)
        if yield_func and gender and gender != "未知":
            yield_func(f"[THOUGHT][预约机器人] 根据性别'{gender}'筛选茶艺师，找到{len(gender_filtered_tms)}位茶艺师\n")

        # 再根据偏好筛选茶艺师
        filtered_tms = self.filter_tea_masters_by_preference(gender_filtered_tms, preference)
        if yield_func and preference and preference != "无":
            yield_func(f"[THOUGHT][预约机器人] 根据偏好'{preference}'进一步筛选，找到{len(filtered_tms)}位茶艺师\n")

        # 查找可用茶艺师
        return self.find_available_tea_master(filtered_tms, gender_filtered_tms, start_time, end_time, preference, gender, yield_func)
