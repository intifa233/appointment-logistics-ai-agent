"""
Web界面路由

处理前端页面渲染和聊天功能
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from api.chat_handler import ProcessUserInput_stream
import logging

# 创建logger实例
logger = logging.getLogger(__name__)
# 模板配置
templates = Jinja2Templates(directory="web/templates")

# Web路由器
router = APIRouter(tags=["Web界面"])

class ChatRequest(BaseModel):
    message: str
    state: str | None = None

@router.get("/", response_class=HTMLResponse, summary="主页")
async def read_root(request: Request):
    """渲染主页聊天界面"""
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/chat/stream", summary="流式聊天")
async def chat_stream_endpoint(chat: ChatRequest):
    """处理流式聊天请求"""
    async def token_generator():
        async for token in ProcessUserInput_stream(chat.message):
            yield token
    return StreamingResponse(token_generator(), media_type="text/plain")

@router.post("/chat", summary="兼容性聊天接口")
async def chat_endpoint(chat: ChatRequest):
    """兼容性聊天接口，建议使用/chat/stream"""
    async def token_generator():
        async for token in ProcessUserInput_stream(chat.message):
            yield token
    return StreamingResponse(token_generator(), media_type="text/plain")

@router.get("/user_behavior", response_class=HTMLResponse, summary="用户行为分析页面")
async def user_behavior_page(request: Request):
    """用户行为分析页面"""
    return templates.TemplateResponse("user_behavior_analysis.html", {"request": request})

@router.get("/knowledge", response_class=HTMLResponse, summary="知识库管理页面")
async def knowledge_page(request: Request):
    """知识库管理页面"""
    # 通过API层获取知识库数据
    try:
        from api.knowledge import get_all_knowledge

        # 调用API层函数获取数据
        knowledge_data = await get_all_knowledge()
        documents = knowledge_data.get("documents", [])
        categories = knowledge_data.get("categories", [])

        return templates.TemplateResponse("knowledge_management.html", {
            "request": request,
            "documents": documents,
            "categories": categories
        })
    except Exception as e:
        return templates.TemplateResponse("knowledge_management.html", {
            "request": request,
            "documents": [],
            "categories": [],
            "error": str(e)
        })

@router.get("/tea-master", response_class=HTMLResponse, summary="茶艺师状态页面")
async def tea_master_page(request: Request):
    """茶艺师状态页面"""
    # 通过API层获取茶艺师数据
    try:
        from api.tea_master import get_all_tea_masters

        # 调用API层函数获取数据
        tea_masters = await get_all_tea_masters()

        return templates.TemplateResponse("tea_master.html", {
            "request": request,
            "tea_masters": tea_masters
        })
    except Exception as e:
        return templates.TemplateResponse("tea_master.html", {
            "request": request,
            "tea_masters": [],
            "error": str(e)
        })

@router.get("/tea-master-schedule", response_class=HTMLResponse, summary="茶艺师排班页面")
async def tea_master_schedule_page(request: Request):
    """茶艺师排班页面"""
    try:
        from api.tea_master import get_all_tea_masters_schedule_today
        from config.time_config import time_config

        # 获取当前日期
        current_date = time_config.current_date_str()

        # 通过API层获取所有茶艺师的排班数据
        schedules_data = await get_all_tea_masters_schedule_today()

        # 构建排班数据格式 - 直接使用API返回的数据
        schedule = []
        for schedule_item in schedules_data:
            schedule.append({
                "id": schedule_item["tea_master_id"],
                "name": schedule_item["tea_master_name"],
                "busy_periods": schedule_item["busy_periods"]
            })

        return templates.TemplateResponse("tea_master_schedule.html", {
            "request": request,
            "schedule": schedule,
            "current_date": current_date
        })
    except Exception as e:
        logger.error(f"加载茶艺师排班数据失败: {str(e)}")
        return templates.TemplateResponse("tea_master_schedule.html", {
            "request": request,
            "schedule": [],
            "error": str(e)
        })

@router.get("/tea-room", response_class=HTMLResponse, summary="茶室管理页面")
async def tea_room_page(request: Request):
    """茶室/包间管理页面"""
    try:
        from api.tea_room import get_all_rooms

        rooms = await get_all_rooms()

        return templates.TemplateResponse("tea_room.html", {
            "request": request,
            "rooms": rooms
        })
    except Exception as e:
        return templates.TemplateResponse("tea_room.html", {
            "request": request,
            "rooms": [],
            "error": str(e)
        })

@router.get("/tea-room-schedule", response_class=HTMLResponse, summary="茶室占用状态页面")
async def tea_room_schedule_page(request: Request):
    """茶室占用状态页面"""
    try:
        from api.tea_room import get_all_rooms_schedule_today
        from config.time_config import time_config

        current_date = time_config.current_date_str()

        schedules_data = await get_all_rooms_schedule_today()

        schedule = []
        for schedule_item in schedules_data:
            schedule.append({
                "id": schedule_item["room_id"],
                "name": schedule_item["room_name"],
                "busy_periods": schedule_item["busy_periods"]
            })

        return templates.TemplateResponse("tea_room_schedule.html", {
            "request": request,
            "schedule": schedule,
            "current_date": current_date
        })
    except Exception as e:
        logger.error(f"加载茶室占用数据失败: {str(e)}")
        return templates.TemplateResponse("tea_room_schedule.html", {
            "request": request,
            "schedule": [],
            "error": str(e)
        })

@router.get("/inventory", response_class=HTMLResponse, summary="茶叶库存管理页面")
async def inventory_page(request: Request):
    """茶叶库存管理页面"""
    try:
        from api.inventory import get_all_items

        result = await get_all_items()
        items = result.get("data", [])
        low_stock_count = sum(
            1 for item in items
            if (item.get("stock_quantity") or 0) <= (item.get("reorder_threshold") or 0)
        )

        return templates.TemplateResponse("inventory.html", {
            "request": request,
            "items": items,
            "low_stock_count": low_stock_count
        })
    except Exception as e:
        logger.error(f"加载库存数据失败: {str(e)}")
        return templates.TemplateResponse("inventory.html", {
            "request": request,
            "items": [],
            "low_stock_count": 0,
            "error": str(e)
        })

@router.get("/user_behavior_analysis", response_class=HTMLResponse, summary="用户行为分析页面")
async def user_behavior_analysis_page(request: Request):
    """用户行为分析页面"""
    return templates.TemplateResponse("user_behavior_analysis.html", {"request": request})

@router.get("/admin", response_class=HTMLResponse, summary="系统管理页面")
async def admin_dashboard(request: Request):
    """系统管理仪表板"""
    try:
        # 通过API层获取系统状态信息
        from api.knowledge import get_all_knowledge
        from api.tea_master import get_all_tea_masters

        # 获取知识库数据
        knowledge_data = await get_all_knowledge()
        knowledge_count = knowledge_data.get("total_count", 0)
        categories = knowledge_data.get("categories", [])

        # 获取茶艺师数据
        tea_masters = await get_all_tea_masters()

        # 数据库信息
        db_info = {
            "knowledge_count": knowledge_count,
            "categories_count": len(categories),
            "tea_masters_count": len(tea_masters),
            "categories": categories
        }

        return templates.TemplateResponse("admin_dashboard.html", {
            "request": request,
            "db_info": db_info,
            "tea_masters": tea_masters[:5]  # 只显示前5位茶艺师
        })
    except Exception as e:
        return templates.TemplateResponse("admin_dashboard.html", {
            "request": request,
            "db_info": {},
            "tea_masters": [],
            "error": str(e)
        })

@router.get("/admin/database", response_class=HTMLResponse, summary="数据库管理页面")
async def database_admin_page(request: Request):
    """数据库管理页面"""
    try:
        # 通过API层获取数据库统计信息
        from api.knowledge import get_all_knowledge
        from api.tea_master import get_all_tea_masters

        # 获取知识库数据
        knowledge_data = await get_all_knowledge()

        # 获取茶艺师数据
        tea_masters = await get_all_tea_masters()

        stats = {
            "knowledge_documents": knowledge_data.get("total_count", 0),
            "categories": len(knowledge_data.get("categories", [])),
            "tea_masters": len(tea_masters),
            "appointments": 0  # TODO: 通过API获取预约数量
        }

        return templates.TemplateResponse("database_admin.html", {
            "request": request,
            "stats": stats
        })
    except Exception as e:
        return templates.TemplateResponse("database_admin.html", {
            "request": request,
            "stats": {},
            "error": str(e)
        })
