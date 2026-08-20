"""
茶艺师API

提供茶艺师信息和排班查询接口
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/api/tea-masters", tags=["茶艺师管理"])


class TeaMasterResponse(BaseModel):
    """茶艺师信息响应"""
    id: int
    name: str
    gender: str
    specialty: str


class ScheduleResponse(BaseModel):
    """排班信息响应"""
    id: int
    tea_master_id: int
    start_time: str
    end_time: str
    status: str
    appointment_id: int | None = None


@router.get("/", response_model=List[TeaMasterResponse], summary="获取所有茶艺师")
async def get_all_tea_masters():
    """获取所有茶艺师信息"""
    try:
        from services.tea_master_service import TeaMasterService
        tea_master_service = TeaMasterService()
        tea_master_service.initialize_default_tea_masters()
        tea_masters = tea_master_service.get_all_tea_masters()

        return [
            TeaMasterResponse(
                id=tm["id"],
                name=tm["name"],
                gender=tm.get("gender", ""),
                specialty=tm.get("specialty", "")
            )
            for tm in tea_masters
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取茶艺师信息失败: {str(e)}")


@router.get("/{tea_master_id}/schedule", response_model=List[ScheduleResponse], summary="获取茶艺师排班")
async def get_tea_master_schedule(tea_master_id: int):
    """获取指定茶艺师今天的排班信息"""
    try:
        from services.tea_master_service import TeaMasterService
        from config.time_config import time_config

        tea_master_service = TeaMasterService()
        tea_master_service.initialize_default_tea_masters()

        # 获取茶艺师信息确认存在
        tm = tea_master_service.get_tea_master_by_id(tea_master_id)
        if not tm:
            raise HTTPException(status_code=404, detail="茶艺师不存在")

        # 获取今天的排班
        today = time_config.today()
        schedules = tea_master_service.get_tea_master_schedules(tea_master_id, today)

        return [
            ScheduleResponse(
                id=sched["id"],
                tea_master_id=sched["tea_master_id"],
                start_time=sched["start_time"].strftime("%H:%M"),
                end_time=sched["end_time"].strftime("%H:%M"),
                status=sched["status"],
                appointment_id=sched.get("appointment_id")
            )
            for sched in schedules
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取排班信息失败: {str(e)}")


@router.get("/{tea_master_id}", response_model=TeaMasterResponse, summary="获取单个茶艺师信息")
async def get_tea_master(tea_master_id: int):
    """获取指定茶艺师的详细信息"""
    try:
        from services.tea_master_service import TeaMasterService

        tea_master_service = TeaMasterService()
        tea_master_service.initialize_default_tea_masters()
        tm = tea_master_service.get_tea_master_by_id(tea_master_id)

        if not tm:
            raise HTTPException(status_code=404, detail="茶艺师不存在")

        return TeaMasterResponse(
            id=tm["id"],
            name=tm["name"],
            gender=tm.get("gender", ""),
            specialty=tm.get("specialty", "")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取茶艺师信息失败: {str(e)}")


@router.get("/schedules/today", summary="获取所有茶艺师今日排班")
async def get_all_tea_masters_schedule_today():
    """获取所有茶艺师今天的排班信息"""
    try:
        from services.tea_master_service import TeaMasterService
        from config.time_config import time_config

        tea_master_service = TeaMasterService()
        tea_master_service.initialize_default_tea_masters()

        # 获取所有茶艺师
        all_tea_masters = tea_master_service.get_all_tea_masters()
        today = time_config.today()

        schedules_data = []
        for tm in all_tea_masters:
            tm_id = tm["id"]
            tm_name = tm["name"]

            # 获取该茶艺师今天的排班
            tm_schedules = tea_master_service.get_tea_master_schedules(tm_id, today)

            busy_periods = []
            for sched in tm_schedules:
                if sched.get("status") == "busy":
                    busy_periods.append({
                        "start": sched["start_time"].strftime("%H:%M") if hasattr(sched["start_time"], 'strftime') else str(sched["start_time"]),
                        "end": sched["end_time"].strftime("%H:%M") if hasattr(sched["end_time"], 'strftime') else str(sched["end_time"]),
                        "appointment_id": sched.get("appointment_id")
                    })

            schedules_data.append({
                "tea_master_id": tm_id,
                "tea_master_name": tm_name,
                "busy_periods": busy_periods
            })

        return schedules_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取排班信息失败: {str(e)}")
