"""
咨询流程处理器

负责协调整个咨询流程
"""

from typing import AsyncGenerator, Dict, Any
from .knowledge_retriever import KnowledgeRetriever
from .consultation_classifier import ConsultationClassifier
from .response_generator import ResponseGenerator


class ConsultationProcessor:
    """咨询流程处理器"""
    
    def __init__(self, knowledge_retriever: KnowledgeRetriever, 
                 consultation_classifier: ConsultationClassifier,
                 response_generator: ResponseGenerator):
        self.knowledge_retriever = knowledge_retriever
        self.consultation_classifier = consultation_classifier
        self.response_generator = response_generator
    
    async def process_consultation(self, user_input: str) -> str:
        """处理标准咨询"""
        # 1. 检索知识
        knowledge_docs = await self.knowledge_retriever.search_knowledge(user_input, top_k=3)
        
        # 2. 生成响应
        response = await self.response_generator.generate_response(user_input, knowledge_docs)
        
        return response
    
    async def process_consultation_stream(self, user_input: str, session_id: str) -> AsyncGenerator[str, None]:
        """处理流式咨询"""
        try:
            # 1. 检索知识
            knowledge_docs = await self.knowledge_retriever.search_knowledge(user_input, top_k=3)
            
            # 2. 生成响应
            async for token in self.response_generator.generate_response_stream(user_input, knowledge_docs):
                yield token
            
            # 3. 记录用户行为
            await self._record_consultation_behavior(user_input, knowledge_docs, session_id)
            
        except Exception as e:
            yield f"[REPLY][咨询机器人]抱歉，处理您的问题时出现了错误：{str(e)}"
    
    async def handle_unrelated_request(self, user_input: str, shared_state) -> AsyncGenerator[str, None]:
        """处理咨询分类器判断为"非咨询类"的请求

        注意：这里不会把请求转发回归类机器人。归类机器人正是把这条消息路由到咨询
        机器人的一方——如果咨询机器人再把它转发回去，遇到两边分类结果持续不一致的
        输入（例如缺乏上下文的短句），会在"归类为咨询任务"和"咨询机器人判定不是
        咨询类问题"之间无限反复调用LLM，形成死循环并持续消耗API配额。
        直接给出兜底回复并把状态交还给分类器即可，不再自动转发。
        """
        # 重置状态，允许下一轮重新分类
        if shared_state:
            from config.constants import StateEnum
            shared_state.value = StateEnum.CLASSIFY

        yield self.response_generator.create_unrelated_message()
    
    async def _record_consultation_behavior(self, user_input: str, knowledge_docs: list, session_id: str):
        """记录咨询行为"""
        try:
            from agents.user_behavior_agent import UserBehaviorAgent
            behavior_agent = UserBehaviorAgent()
            
            action_data = {
                'question': user_input,
                'knowledge_docs_used': len(knowledge_docs),
                'categories': list(set(doc.get('category', 'unknown') for doc in knowledge_docs)) if knowledge_docs else []
            }
            
            behavior_agent.record_behavior(
                action_type='consultation',
                action_data=action_data,
                session_id=session_id
            )
            
        except Exception as behavior_error:
            print(f"记录咨询行为失败：{behavior_error}")
