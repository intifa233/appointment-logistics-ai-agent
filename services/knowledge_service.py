# services/knowledge_service.py

import numpy as np
import faiss
from typing import List, Dict, Tuple, Optional
from db.db_router import DatabaseRouter
from .text_embedding import embed_input
import logging

logger = logging.getLogger(__name__)

class KnowledgeService:
    """知识库服务类 - 结合数据库存储和向量检索"""
    
    def __init__(self, db_path: str = 'sqlite:///data/tea_house.db'):
        # 使用统一的DatabaseRouter，符合架构设计
        self.db_router = DatabaseRouter(db_path)
        self.db = self.db_router.knowledge  # 通过router访问knowledge repository
        self.index = None
        self.document_ids = []  # 维护文档ID与索引位置的映射
        self.initialized = False

        # 默认知识库内容
        self.default_knowledge = [
            {
                "content": "我们茶馆的营业时间是每天上午10点到晚上11点，全年无休。",
                "category": "营业时间",
                "keywords": ["营业时间", "开门", "关门", "几点", "时间"]
            },
            {
                "content": "我们提供多种茶室与茶艺服务：雅座品茶（38元/位，含2小时茶位费）、包间茶艺（198元/2小时起，含专属茶艺师）、茶道体验室仪式课（288元/1.5小时，含茶艺师讲解）。",
                "category": "服务项目",
                "keywords": ["服务", "茶艺", "包间", "雅座", "价格", "收费", "多少钱"]
            },
            {
                "content": "我们有专业的男女茶艺师为您服务。所有茶艺师都经过专业培训，持有评茶员或茶艺师资格证书。您可以根据个人喜好选择男茶艺师或女茶艺师，也可以指定擅长某类茶（如普洱、乌龙）的茶艺师。",
                "category": "茶艺师信息",
                "keywords": ["茶艺师", "师傅", "男", "女", "专业", "资格"]
            },
            {
                "content": "我们茶馆的位置位于北京海淀区中关村大街27号，交通便利，地铁2号线A口向北步行100米即可到达",
                "category": "门店地址",
                "keywords": ["地址", "门店信息", "到达方式", "交通", "位置", "在哪", "怎么走", "怎么去", "地铁", "路线"]
            },
            {
                "content": "绿茶（如西湖龙井、太平猴魁）滋味清爽鲜嫩，性凉，能提神醒脑、生津止渴，特别适合夏季或需要提神的场合。",
                "category": "茶叶介绍",
                "keywords": ["绿茶", "龙井", "效果", "作用", "好处", "适合"]
            },
            {
                "content": "普洱茶分生茶和熟茶：生茶滋味较为清爽带涩，越陈越香；熟茶经渥堆发酵，口感醇厚温和，性温，适合肠胃较弱或秋冬季节饮用。",
                "category": "茶叶介绍",
                "keywords": ["普洱", "生茶", "熟茶", "陈化", "肠胃", "温和"]
            },
            {
                "content": "花茶（如茉莉花茶）在绿茶或红茶基础上窨制花香，香气怡人，口感清雅，适合喜欢淡雅香气、想放松心情的客人。",
                "category": "茶叶介绍",
                "keywords": ["花茶", "茉莉", "香气", "放松", "适合"]
            },
            {
                "content": "我们的茶艺师都有3年以上的专业经验，定期接受茶艺与礼仪培训以确保服务质量。我们注重客户体验，力求为每位客户提供最舒适的品茶氛围。",
                "category": "服务质量",
                "keywords": ["经验", "专业", "培训", "质量", "舒适"]
            },
            {
                "content": "如需取消或更改预约，请提前至少2小时通知我们。临时取消可能会产生一定的茶位费用。",
                "category": "预约政策",
                "keywords": ["取消", "更改", "改期", "退约", "政策"]
            },
            {
                "content": "我们提供会员卡服务，充值500元送50元，充值1000元送150元。会员还可享受包间预约优先权和生日专属茶点。",
                "category": "会员服务",
                "keywords": ["会员", "充值", "优惠", "折扣", "生日"]
            }
        ]

    async def initialize(self):
        """初始化知识库服务"""
        try:
            # 检查数据库中是否已有数据
            existing_docs = self.db.get_all_documents()
            
            if not existing_docs:
                logger.info("数据库为空，初始化默认知识库")
                await self._create_default_knowledge()
            else:
                logger.info(f"从数据库加载了 {len(existing_docs)} 条知识")
            
            # 构建向量索引
            await self._build_vector_index()
            self.initialized = True
            logger.info("知识库服务初始化完成")
            
        except Exception as e:
            logger.error(f"知识库服务初始化失败: {e}")
            raise

    async def _create_default_knowledge(self):
        """创建默认知识库"""
        for knowledge in self.default_knowledge:
            try:
                # 生成嵌入向量
                text_for_embedding = f"{knowledge['content']} {' '.join(knowledge['keywords'])}"
                embedding = embed_input(text_for_embedding)
                
                # 保存到数据库
                self.db.add_document(
                    content=knowledge['content'],
                    category=knowledge['category'],
                    keywords=knowledge['keywords'],
                    embedding=embedding
                )
                logger.debug(f"添加默认知识: {knowledge['content'][:50]}...")
                
            except Exception as e:
                logger.error(f"添加默认知识失败: {e}")

    async def _build_vector_index(self):
        """构建向量索引"""
        try:
            documents = self.db.get_all_documents()
            if not documents:
                logger.warning("没有文档可用于构建索引")
                return

            embeddings = []
            self.document_ids = []
            
            for doc in documents:
                if doc.get('embedding'):
                    embeddings.append(doc['embedding'])
                    self.document_ids.append(doc['id'])
                else:
                    # 如果没有嵌入向量，生成一个
                    logger.warning(f"文档 {doc['id']} 缺少嵌入向量，正在生成...")
                    text_for_embedding = f"{doc['content']} {' '.join(doc.get('keywords', []))}"
                    embedding = embed_input(text_for_embedding)
                    
                    # 更新数据库
                    self.db.update_document(doc['id'], embedding=embedding)
                    
                    embeddings.append(embedding)
                    self.document_ids.append(doc['id'])

            if embeddings:
                # 创建FAISS索引
                embeddings_array = np.array(embeddings).astype('float32')
                dimension = embeddings_array.shape[1]
                self.index = faiss.IndexFlatIP(dimension)  # 内积相似度
                self.index.add(embeddings_array)
                logger.info(f"构建向量索引完成，包含 {len(embeddings)} 个向量")
            else:
                logger.warning("没有有效的嵌入向量，无法构建索引")

        except Exception as e:
            logger.error(f"构建向量索引失败: {e}")
            raise

    async def search(self, query: str, top_k: int = 3, category: str = None) -> List[Dict]:
        """搜索相关文档

        对纯向量语义检索做了关键词命中加权（混合检索）：短查询（如"茶室位置"）
        在纯embedding相似度下有时会因为字面重合（如"茶室"二字）把不相关文档排到
        真正相关文档前面。这里在语义分数基础上叠加一个基于category/keywords的
        字面命中加权，让明确匹配到关键词的文档更容易进入top_k。
        """
        if not self.initialized or self.index is None:
            logger.warning("知识库服务未初始化或索引不可用")
            return []

        try:
            # 生成查询的嵌入向量
            query_embedding = embed_input(query)
            query_array = np.array([query_embedding]).astype('float32')

            # 扩大候选池，避免关键词命中的文档因为语义分数稍低而被提前截断
            candidate_count = min(max(top_k * 3, 8), len(self.document_ids))
            scores, indices = self.index.search(query_array, candidate_count)

            candidates = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.document_ids):
                    doc_id = self.document_ids[idx]
                    doc = self.db.get_document(doc_id)

                    if doc:
                        # 如果指定了分类过滤
                        if category and doc.get('category') != category:
                            continue

                        semantic_score = float(score)
                        boost = self._keyword_boost(query, doc)
                        doc['score'] = semantic_score
                        candidates.append((semantic_score + boost, doc))

            # 按“语义分数 + 关键词加权”重新排序
            candidates.sort(key=lambda item: item[0], reverse=True)

            results = []
            for _, doc in candidates[:top_k]:
                doc['rank'] = len(results) + 1
                results.append(doc)

            return results

        except Exception as e:
            logger.error(f"搜索知识库失败: {e}")
            return []

    def _keyword_boost(self, query: str, doc: Dict) -> float:
        """基于分类名/关键词与查询的字面重合度计算加权分数

        每命中一个关键词或分类名加 0.2 分（封顶 0.4），用于弥补短查询下
        纯向量语义检索区分度不足的问题。
        """
        boost = 0.0
        category = (doc.get('category') or '').strip()
        if category and (category in query or query in category):
            boost += 0.2

        for keyword in doc.get('keywords') or []:
            keyword = (keyword or '').strip()
            if keyword and (keyword in query or query in keyword):
                boost += 0.2

        return min(boost, 0.4)

    async def add_document(self, content: str, category: str, keywords: List[str] = None) -> bool:
        """添加新文档"""
        try:
            if keywords is None:
                keywords = []
            
            # 生成嵌入向量
            text_for_embedding = f"{content} {' '.join(keywords)}"
            embedding = embed_input(text_for_embedding)
            
            # 保存到数据库
            doc_id = self.db.add_document(content, category, keywords, embedding)
            
            # 重建索引
            await self._build_vector_index()
            
            logger.info(f"成功添加文档 {doc_id}: {content[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            return False

    async def update_document(self, doc_id: int, content: str = None, category: str = None, keywords: List[str] = None) -> bool:
        """更新文档"""
        try:
            # 如果更新了内容或关键词，需要重新生成嵌入向量
            embedding = None
            if content is not None or keywords is not None:
                # 获取当前文档信息
                current_doc = self.db.get_document(doc_id)
                if not current_doc:
                    return False
                
                # 使用新值或保持原值
                final_content = content if content is not None else current_doc['content']
                final_keywords = keywords if keywords is not None else current_doc.get('keywords', [])
                
                # 生成新的嵌入向量
                text_for_embedding = f"{final_content} {' '.join(final_keywords)}"
                embedding = embed_input(text_for_embedding)
            
            # 更新数据库
            success = self.db.update_document(doc_id, content, category, keywords, embedding)
            
            if success and embedding is not None:
                # 重建索引
                await self._build_vector_index()
            
            return success
            
        except Exception as e:
            logger.error(f"更新文档失败: {e}")
            return False

    async def delete_document(self, doc_id: int, soft_delete: bool = True) -> bool:
        """删除文档"""
        try:
            success = self.db.delete_document(doc_id, soft_delete)
            
            if success:
                # 重建索引
                await self._build_vector_index()
            
            return success
            
        except Exception as e:
            logger.error(f"删除文档失败: {e}")
            return False

    def get_all_documents(self, include_inactive: bool = False) -> List[Dict]:
        """获取所有文档"""
        return self.db.get_all_documents(include_inactive)

    def get_document(self, doc_id: int) -> Dict:
        """获取指定文档"""
        return self.db.get_document(doc_id)

    def get_all_categories(self) -> List[str]:
        """获取所有分类"""
        return self.db.get_all_categories()

    def get_documents_count(self) -> int:
        """获取文档总数"""
        return self.db.get_documents_count()

    def search_by_category(self, category: str) -> List[Dict]:
        """按分类搜索文档"""
        return self.db.search_documents_by_category(category)

    def search_by_keywords(self, keywords: List[str]) -> List[Dict]:
        """按关键词搜索文档"""
        return self.db.search_documents_by_keywords(keywords)
