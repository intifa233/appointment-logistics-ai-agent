"""
FastAPI应用程序

主应用程序入口，配置中间件、路由和异常处理
自动初始化知识库、茶艺师、茶室和库存数据
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from services.knowledge_service import KnowledgeService
from services.tea_master_service import TeaMasterService
from services.tea_room_service import TeaRoomService
from services.inventory_service import InventoryService
from services.recommendation_service import RecommendationService
from typing import List, Optional
import logging
import asyncio

# 导入路由
from api import api_routers
from api.core.exceptions import api_exception_handler, general_exception_handler, BusinessException
from web import router as web_router

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic模型
from pydantic import BaseModel

class KnowledgeRequest(BaseModel):
    content: str
    category: str
    keywords: List[str] = []

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    category: Optional[str] = None

async def initialize_system():
    """系统启动时自动初始化"""
    try:
        logger.info("🚀 正在初始化智能茶馆预约系统...")

        # 初始化知识库服务
        logger.info("📚 初始化知识库服务...")
        knowledge_service = KnowledgeService()
        await knowledge_service.initialize()

        # 初始化茶艺师服务
        logger.info("🍵 初始化茶艺师服务...")
        tea_master_service = TeaMasterService()
        tea_master_service.initialize_default_tea_masters()

        # 初始化茶室服务
        logger.info("🏮 初始化茶室服务...")
        tea_room_service = TeaRoomService()
        tea_room_service.initialize_default_rooms()

        # 初始化库存服务
        logger.info("📦 初始化茶叶库存服务...")
        inventory_service = InventoryService()
        inventory_service.initialize_default_items()

        # 初始化推荐服务
        logger.info("🎯 启动推荐调度服务...")
        recommendation_service = RecommendationService()
        if recommendation_service.start_scheduler():
            logger.info("✅ 推荐调度服务启动成功")
        else:
            logger.warning("⚠️ 推荐调度服务启动失败")
        
        logger.info("✅ 系统初始化完成！")
        
    except Exception as e:
        logger.error(f"❌ 系统初始化失败: {e}")
        raise

def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    
    app = FastAPI(
        title="茶馆智能预约AI代理",
        description="提供茶室预约管理、茶艺咨询、库存与排班管理、用户行为分析等功能的API服务",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境中应该设置具体的域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册异常处理器
    app.add_exception_handler(BusinessException, api_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # 注册API路由
    for router in api_routers:
        app.include_router(router)

    # 注册Web界面路由
    app.include_router(web_router)

    # 静态文件
    app.mount("/static", StaticFiles(directory="web/static"), name="static")

    # 健康检查（供 Railway / Render 等云平台探活使用）
    @app.get("/health", include_in_schema=False)
    async def health_check():
        return {"status": "ok"}

    # 添加启动事件
    @app.on_event("startup")
    async def startup_event():
        """应用启动时自动初始化系统"""
        await initialize_system()

    return app

# 创建应用实例
app = create_app()

if __name__ == "__main__":
    import os
    import uvicorn
    # 云平台（如 Railway）会通过 PORT 环境变量注入监听端口，且要求绑定 0.0.0.0
    # 而不是 127.0.0.1，否则平台的负载均衡无法连接到容器内的服务。
    port = int(os.getenv("PORT", "8001"))
    # proxy_headers + forwarded_allow_ips：信任云平台（Railway等）转发的
    # X-Forwarded-Proto 等头，否则应用会以为自己收到的是纯HTTP连接，
    # 生成的重定向（如FastAPI的自动尾斜杠重定向）会是http://而非https://，
    # 导致浏览器把它当作混合内容拦截，接口请求"卡住"没有任何报错。
    uvicorn.run(app, host="0.0.0.0", port=port, proxy_headers=True, forwarded_allow_ips="*")
