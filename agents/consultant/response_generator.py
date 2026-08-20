"""
响应生成器

负责生成AI响应内容
"""

from typing import Dict, Any, AsyncGenerator
from langchain_core.language_models.chat_models import BaseChatModel
from .prompt_builder import PromptBuilder


class ResponseGenerator:
    """响应生成器"""
    
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.prompt_builder = PromptBuilder()
    
    async def generate_response(self, user_input: str, knowledge_docs: list) -> str:
        """生成标准响应"""
        try:
            prompt = self.prompt_builder.build_consultation_prompt(user_input, knowledge_docs)
            response = await self.llm.ainvoke([{"role": "user", "content": prompt}])
            return response.content
        except Exception as e:
            return f"抱歉，处理您的问题时出现了错误。请稍后再试。"
    
    async def generate_response_stream(self, user_input: str, knowledge_docs: list) -> AsyncGenerator[str, None]:
        """生成流式响应"""
        try:
            prompt = self.prompt_builder.build_consultation_prompt(user_input, knowledge_docs)
            response = await self.llm.ainvoke([{"role": "user", "content": prompt}])
            content = response.content
            
            # 只在开头添加一次REPLY标签，然后逐字符输出
            yield "[REPLY][咨询机器人]"
            for char in content:
                yield char
                
        except Exception as e:
            error_msg = f"抱歉，处理您的问题时出现了错误：{str(e)}"
            yield "[REPLY][咨询机器人]"
            for char in error_msg:
                yield char
    
    def create_unrelated_message(self) -> str:
        """创建无法回答该问题时的兜底回复

        注意：这里直接给出最终回复，不再转发回归类机器人 —— 归类机器人正是把这条
        消息路由到咨询机器人的一方，如果再转发回去，会在两者之间反复横跳形成死循环。
        """
        return ("[REPLY][咨询机器人]抱歉，这个问题我目前还没法回答。"
                "您可以换个问法，或者直接问问茶艺服务、预约、价格、营业时间等相关内容，我很乐意为您解答。")
