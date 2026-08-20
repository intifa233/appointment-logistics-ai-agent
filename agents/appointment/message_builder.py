"""
消息构建器

负责构建各种响应消息
"""

from typing import Dict, Any, List


class MessageBuilder:
    """消息构建器"""

    def __init__(self):
        self.missing_info_prompts = {
            "gender": "您希望选择男茶艺师还是女茶艺师呢？",
            "start_time": "请问您想预约的时间是？",
            "duration": "请问您需要多长时间的茶室服务？",
            "project": "请问您需要什么服务项目？比如品茶、茶道体验？",
            "preference": "您对茶艺师的讲解节奏有偏好吗？",
            "wants_tea_master": "请问您需要我们为您安排一位专属茶艺师吗？如果不需要，我们也可以直接为您安排茶座～"
        }

    def create_appointment_success_message(self, tm: Dict[str, Any] = None, room: Dict[str, Any] = None) -> str:
        """创建预约成功消息"""
        room_suffix = f"为您安排的茶室是{room['name']}（{room.get('room_type', '')}）。" if room else ""

        # 未指定/不需要专属茶艺师
        if not tm:
            return (f"\n机器人：已为您安排好品茶时间，预约成功！{room_suffix}"
                    "今天下午北京最高温度39℃，出行请注意防晒，期待与您相遇\n")
        # 检查是否是推荐茶艺师
        if tm.get('is_recommendation'):
            original_tm = tm.get('original_tea_master', {})
            return (f"\n机器人：已为您预约茶艺师：{tm['name']}，性别：{tm['gender']}。预约成功！"
                    f"（原指定的{original_tm.get('name', '')}茶艺师时间冲突，{tm['name']}在相同茶艺方面同样专业）{room_suffix}"
                    "今天下午北京最高温度39℃，出行请注意防晒，期待与您相遇\n")
        else:
            return (f"\n机器人：已为您预约茶艺师：{tm['name']}，性别：{tm['gender']}。预约成功！{room_suffix}"
                    "今天下午北京最高温度39℃，出行请注意防晒，期待与您相遇\n")

    def create_tea_master_recommendation_message(self, original_tm: Dict[str, Any],
                                               recommended_tm: Dict[str, Any],
                                               appointment_history: Dict[str, Any],
                                               llm=None) -> str:
        """创建茶艺师推荐消息，使用LLM生成个性化措辞"""
        project = appointment_history.get('project', '品茶服务')
        start_time = appointment_history.get('start_time', '')

        if llm:
            try:
                # 构建LLM提示
                prompt = f"""
作为一个专业的预约助手，用户想预约{original_tm['name']}茶艺师做{project}，但{original_tm['name']}茶艺师在{start_time}这个时间段不空闲。

我找到了一位相似的茶艺师：
- 姓名：{recommended_tm['name']}
- 性别：{recommended_tm['gender']}
- 专长：{recommended_tm.get('specialty', '')}

原茶艺师专长：{original_tm.get('specialty', '')}

请帮我生成一段温馨、专业的推荐话术，告诉用户原茶艺师没空，但推荐茶艺师在相同茶艺方面同样专业，这个时间段有空，询问用户是否愿意预约推荐茶艺师。

要求：
1. 语气温和、专业
2. 突出推荐茶艺师的专业性
3. 明确询问用户意愿
4. 字数控制在80字以内
"""

                response = llm.invoke(prompt)
                if hasattr(response, 'content'):
                    generated_msg = response.content.strip()
                    if generated_msg:
                        return f"\n机器人：{generated_msg}\n"

            except Exception as e:
                print(f"LLM生成推荐消息失败: {e}")

        # 如果LLM失败，使用默认消息
        return (f"\n机器人：抱歉，{original_tm['name']}茶艺师在{start_time}这个时间段不空闲。"
                f"不过{recommended_tm['name']}茶艺师（{recommended_tm['gender']}）在{project}方面同样专业，"
                f"这个时间段有空，请问您愿意让我帮您预约{recommended_tm['name']}茶艺师吗？\n")

    def create_recommendation_declined_message(self, llm=None) -> str:
        """创建用户拒绝推荐时的消息"""
        if llm:
            try:
                prompt = """
用户拒绝了我推荐的茶艺师，请帮我生成一段专业、温馨的回复，表达理解并提供其他选择建议。

要求：
1. 表达理解用户的选择
2. 提供其他解决方案（如换时间、重新选择等）
3. 保持专业和友好的语气
4. 字数控制在60字以内
"""
                response = llm.invoke(prompt)
                if hasattr(response, 'content'):
                    generated_msg = response.content.strip()
                    if generated_msg:
                        return f"\n机器人：{generated_msg}\n"
            except Exception as e:
                print(f"LLM生成拒绝消息失败: {e}")

        # 默认消息
        return "\n机器人：好的，我理解您的选择。您可以选择其他时间段，或者我可以为您重新推荐其他茶艺师。请问您还有其他需要吗？\n"

    def create_appointment_failure_message(self, tea_master_name: str) -> str:
        """创建预约失败消息"""
        if tea_master_name and tea_master_name != "未知":
            # 通过Services层访问数据库
            from services.appointment_service import AppointmentService
            appointment_service = AppointmentService()
            specific_tm = appointment_service.get_tea_master_by_name(tea_master_name)
            if specific_tm:
                return f"\n机器人：抱歉，{tea_master_name}茶艺师在您选择的时间段不空闲。请选择其他时间，或者我可以为您推荐其他茶艺师。\n"
            else:
                return f"\n机器人：抱歉，没有找到名为'{tea_master_name}'的茶艺师。请确认茶艺师姓名，或者我可以为您推荐其他茶艺师。\n"
        else:
            return "\n机器人：抱歉，该时间段没有合适的茶艺师空闲，请选择其他时间或调整偏好。\n"

    def create_missing_info_questions(self, missing_info: List[str]) -> str:
        """根据缺失信息创建询问"""
        questions = [self.missing_info_prompts.get(field, f"请补充{field}信息") for field in missing_info]
        return "\n" + " ".join(questions) + "\n"

    def create_unrelated_message(self) -> str:
        """创建无关请求的消息"""
        return "[REPLY][预约机器人]抱歉，我无法处理这个问题。我只能帮您处理茶艺预约服务相关的事情。请问您需要预约茶室或茶艺师吗？\n"

    def create_parse_error_message(self) -> str:
        """创建解析错误消息"""
        return "[REPLY][预约机器人]\n机器人：解析失败，请重试。\n"

    def create_save_failure_message(self) -> str:
        """创建保存失败消息"""
        return "\n机器人：抱歉，预约保存失败，请重试。\n"
