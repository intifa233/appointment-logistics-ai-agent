"""
茶室API

提供茶室/包间信息和排班查询接口
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/tea-rooms", tags=["茶室管理"])


class TeaRoomResponse(BaseModel):
    """茶室信息响应"""
    id: int
    name: str
    room_type: Optional[str] = None
    capacity: Optional[int] = None
    equipment: Optional[List[str]] = None
    status: Optional[str] = None


class RoomScheduleResponse(BaseModel):
    """茶室排班信息响应"""
    id: int
    room_id: int
    start_time: str
    end_time: str
    status: str
    appointment_id: int | None = None


@router.get("/", response_model=List[TeaRoomResponse], summary="获取所有茶室")
async def get_all_rooms():
    """获取所有茶室信息"""
    try:
        from services.tea_room_service import TeaRoomService
        tea_room_service = TeaRoomService()
        tea_room_service.initialize_default_rooms()
        rooms = tea_room_service.get_all_rooms()

        return [TeaRoomResponse(**room) for room in rooms]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取茶室信息失败: {str(e)}")


@router.get("/{room_id}/schedule", response_model=List[RoomScheduleResponse], summary="获取茶室排班")
async def get_room_schedule(room_id: int):
    """获取指定茶室今天的排班信息"""
    try:
        from services.tea_room_service import TeaRoomService
        from config.time_config import time_config

        tea_room_service = TeaRoomService()
        tea_room_service.initialize_default_rooms()

        room = tea_room_service.get_room_by_id(room_id)
        if not room:
            raise HTTPException(status_code=404, detail="茶室不存在")

        today = time_config.today()
        schedules = tea_room_service.get_room_schedules(room_id, today)

        return [
            RoomScheduleResponse(
                id=sched["id"],
                room_id=sched["room_id"],
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


@router.get("/{room_id}", response_model=TeaRoomResponse, summary="获取单个茶室信息")
async def get_room(room_id: int):
    """获取指定茶室的详细信息"""
    try:
        from services.tea_room_service import TeaRoomService

        tea_room_service = TeaRoomService()
        tea_room_service.initialize_default_rooms()
        room = tea_room_service.get_room_by_id(room_id)

        if not room:
            raise HTTPException(status_code=404, detail="茶室不存在")

        return TeaRoomResponse(**room)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取茶室信息失败: {str(e)}")


@router.get("/schedules/today", summary="获取所有茶室今日排班")
async def get_all_rooms_schedule_today():
    """获取所有茶室今天的排班信息"""
    try:
        from services.tea_room_service import TeaRoomService
        from config.time_config import time_config

        tea_room_service = TeaRoomService()
        tea_room_service.initialize_default_rooms()

        all_rooms = tea_room_service.get_all_rooms()
        today = time_config.today()

        schedules_data = []
        for room in all_rooms:
            room_id = room["id"]
            room_schedules = tea_room_service.get_room_schedules(room_id, today)

            busy_periods = []
            for sched in room_schedules:
                if sched.get("status") == "busy":
                    busy_periods.append({
                        "start": sched["start_time"].strftime("%H:%M") if hasattr(sched["start_time"], 'strftime') else str(sched["start_time"]),
                        "end": sched["end_time"].strftime("%H:%M") if hasattr(sched["end_time"], 'strftime') else str(sched["end_time"]),
                        "appointment_id": sched.get("appointment_id")
                    })

            schedules_data.append({
                "room_id": room_id,
                "room_name": room["name"],
                "busy_periods": busy_periods
            })

        return schedules_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取排班信息失败: {str(e)}")
