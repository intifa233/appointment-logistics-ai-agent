"""
用户输入解析器

负责解析用户输入并提取预约相关信息
"""

import json
from typing import Dict, Any, Generator
from langchain.prompts import PromptTemplate
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage


class InputParser:
    """用户输入解析器"""
    
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.prompt = self._create_prompt_template()
        self.chain = self.prompt | self.llm
    
    def _create_prompt_template(self) -> PromptTemplate:
        """创建预约信息提取的Prompt模板"""
        from config.time_config import time_config
        current_date = time_config.current_date_str()
        current_datetime = time_config.current_datetime_str()
        
        return PromptTemplate(
            input_variables=["history", "user_input"],
            template=(
                "你是一个预约机器人，负责帮用户预约茶室与茶艺师服务。\n"
                f"当前日期是{current_date}，当前北京时间是{current_datetime}。\n"
                "当前已知信息：{history}\n"
                "用户输入：{user_input}\n"
                "特别注意：如果用户输入是对推荐茶艺师确认问题的回应（如\"是\"、\"好\"、\"可以\"、\"不\"、\"不要\"等简短回复），请优先识别为confirmation，而不要标记为unrelated。\n"
                "重要：请你只输出纯JSON格式，不要添加任何markdown标记如```json或```，不要添加任何其他文字说明，直接输出JSON：\n"
                "{{\n"
                '  "gender": "茶艺师性别（如男/女/未知）",\n'
                '  "start_time": "预约起始时间，必须转换为标准格式YYYY-MM-DD HH:MM。如果用户说今天下午3点，转换为当前日期 15:00；如果说明天上午10点，转换为明天日期 10:00。如果只说时间没说日期，默认为今天。如果完全没有时间信息则为未知",\n'
                '  "duration": "服务时长，统一转换为分钟数格式，如180分钟、60分钟。如果没有明确时长则为未知",\n'
                '  "project": "服务项目（如品茶/茶道体验/茶艺培训/未知）",\n'
                '  "guest_count": "预约人数，只保留数字（如1、2、4）。如果用户说\'我们两个人\'\'4位\'\'一家三口\'等，请换算成数字；如果完全没提到人数则为未知",\n'
                '  "preference": "用户倾向（如讲解细致/节奏轻松/无）",\n'
                '  "tea_master_name": "指定茶艺师姓名（如果用户明确提到茶艺师名字，如张伟、李娜等，否则为未知）",\n'
                '  "wants_tea_master": "用户是否需要专属茶艺师服务：如果用户明确表示需要/想要/请安排茶艺师，则为需要；如果用户明确表示不需要/不用/不用麻烦/随便/直接安排位置就行，则为不需要；如果用户完全没提及是否需要茶艺师，则为未知",\n'
                '  "confirmation": "如果用户在回应茶艺师推荐的确认问题，提取用户的回复内容（如是/好/可以/不/不要等），否则为未知",\n'
                '  "info_complete": "根据实际情况判断：start_time、project、duration、guest_count始终是必需信息；此外1)如果指定了茶艺师名且不为未知，不需要额外信息；2)如果没指定茶艺师名且wants_tea_master为不需要，不需要额外信息；3)如果没指定茶艺师名且wants_tea_master为需要，还需要gender不为未知；4)如果没指定茶艺师名且wants_tea_master未知，还需要wants_tea_master不为未知。只有上述所有必需字段都不是未知时，info_complete才为true",\n'
                '  "unrelated": "如果用户的问题和预约无关（如问天气、聊天等），则为true，否则为false。注意：对推荐茶艺师的确认回复（是/不等）不应标记为unrelated",\n'
                '  "missing_info": "如果info_complete为false，请列出缺少的关键信息，如[start_time, project]等"\n'
                "}}\n"
                "判断逻辑：\n"
                "1. 如果用户明确指定了茶艺师姓名（如\"张伟茶艺师\"、\"预约李娜\"等），请务必提取tea_master_name，此时视为wants_tea_master为需要\n"
                "2. 如果用户在回应推荐茶艺师的确认问题（如回复\"是\"、\"好\"、\"可以\"、\"不\"、\"不要\"等），请提取到confirmation字段，并且不要将其标记为unrelated\n"
                "3. 必需信息判断：start_time、project、duration、guest_count 始终是必需的\n"
                "   - 如果指定了茶艺师名：无需额外信息\n"
                "   - 如果没指定茶艺师名，且wants_tea_master为不需要：无需额外信息\n"
                "   - 如果没指定茶艺师名，且wants_tea_master为需要：还需要gender\n"
                "   - 如果没指定茶艺师名，且wants_tea_master未知：还需要wants_tea_master（应先询问用户是否需要专属茶艺师）\n"
                "4. 只有当所有必需信息都不是'未知'时，info_complete才为true\n"
                "5. 如果用户的问题和预约无关，请将unrelated设为true\n"
                "再次强调：只输出纯JSON，不要有任何代码块标记或其他文字。"
            )
        )
    
    def parse_stream(self, user_input: str, chat_history: InMemoryChatMessageHistory) -> Generator[str, None, str]:
        """流式解析用户输入"""
        # 添加用户消息到历史
        chat_history.add_message(HumanMessage(content=user_input))
        
        # 构建历史字符串
        history_str = "\n".join(
            [f"用户：{m.content}" if m.type == "human" else f"机器人：{m.content}" 
             for m in chat_history.messages]
        )
        
        # 流式调用LLM
        response_stream = self.chain.stream({"history": history_str, "user_input": user_input})
        ai_content = ""
        
        for chunk in response_stream:
            token = chunk.content if hasattr(chunk, "content") else str(chunk)
            ai_content += token
            yield token
        
        # 添加AI回复到历史
        chat_history.add_message(AIMessage(content=ai_content))
        return ai_content
    
    def parse_data(self, ai_content: str) -> Dict[str, Any]:
        """解析AI返回的JSON数据"""
        try:
            return json.loads(ai_content)
        except json.JSONDecodeError:
            return {
                "gender": "未知",
                "start_time": "未知",
                "duration": "未知",
                "project": "未知",
                "guest_count": "未知",
                "preference": "未知",
                "tea_master_name": "未知",
                "wants_tea_master": "未知",
                "confirmation": "未知",
                "info_complete": False,
                "unrelated": False,
                "missing_info": ["所有信息"]
            }
