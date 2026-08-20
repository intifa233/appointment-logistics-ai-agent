"""
茶叶库存管理API

查询接口对所有人开放；新增/编辑/删除/调整库存等写操作
需要在请求头 X-Employee-Id 中提供有效的员工编号（CC001 - CC010）。
"""

from fastapi import APIRouter, HTTPException, Header, Depends
from typing import List, Optional
from pydantic import BaseModel
from config.constants import AUTHORIZED_INVENTORY_EDITOR_IDS

router = APIRouter(prefix="/api/inventory", tags=["库存管理"])


class InventoryItem(BaseModel):
    name: str
    category: Optional[str] = None
    unit: Optional[str] = None
    stock_quantity: float = 0
    reorder_threshold: float = 0
    unit_price: Optional[float] = None


def verify_employee_id(x_employee_id: Optional[str] = Header(default=None, alias="X-Employee-Id")) -> str:
    """校验编辑库存所需的员工编号（CC001 - CC010）"""
    employee_id = (x_employee_id or "").strip().upper()
    if employee_id not in AUTHORIZED_INVENTORY_EDITOR_IDS:
        raise HTTPException(
            status_code=403,
            detail="员工编号无效或未提供，无权限编辑库存（请在请求头 X-Employee-Id 中提供 CC001-CC010 之间的编号）"
        )
    return employee_id


@router.get("/")
async def get_all_items():
    """获取所有库存项"""
    try:
        from services.inventory_service import InventoryService
        inventory_service = InventoryService()
        inventory_service.initialize_default_items()
        items = inventory_service.get_all_items()
        return {
            "status": "success",
            "data": items,
            "total_count": len(items)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取库存信息失败: {str(e)}")


@router.get("/low-stock")
async def get_low_stock_items():
    """获取库存低于补货阈值的项目"""
    try:
        from services.inventory_service import InventoryService
        inventory_service = InventoryService()
        inventory_service.initialize_default_items()
        items = inventory_service.get_low_stock_items()
        return {
            "status": "success",
            "data": items,
            "total_count": len(items)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取低库存信息失败: {str(e)}")


@router.get("/{item_id}")
async def get_item(item_id: int):
    """获取指定库存项"""
    try:
        from services.inventory_service import InventoryService
        inventory_service = InventoryService()
        item = inventory_service.get_item_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="库存项不存在")
        return {"status": "success", "data": item}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取库存项失败: {str(e)}")


@router.post("/")
async def add_item(item: InventoryItem, employee_id: str = Depends(verify_employee_id)):
    """新增库存项（需要有效员工编号）"""
    try:
        from services.inventory_service import InventoryService
        inventory_service = InventoryService()
        item_id = inventory_service.add_item(
            name=item.name,
            category=item.category,
            unit=item.unit,
            stock_quantity=item.stock_quantity,
            reorder_threshold=item.reorder_threshold,
            unit_price=item.unit_price
        )
        return {"status": "success", "message": "库存项添加成功", "data": {"id": item_id}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加库存项失败: {str(e)}")


@router.put("/{item_id}")
async def update_item(item_id: int, item: InventoryItem, employee_id: str = Depends(verify_employee_id)):
    """更新库存项（需要有效员工编号）"""
    try:
        from services.inventory_service import InventoryService
        inventory_service = InventoryService()
        result = inventory_service.update_item(
            item_id,
            name=item.name,
            category=item.category,
            unit=item.unit,
            stock_quantity=item.stock_quantity,
            reorder_threshold=item.reorder_threshold,
            unit_price=item.unit_price
        )
        if not result:
            raise HTTPException(status_code=404, detail="库存项不存在")
        return {"status": "success", "message": "库存项更新成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新库存项失败: {str(e)}")


@router.delete("/{item_id}")
async def delete_item(item_id: int, employee_id: str = Depends(verify_employee_id)):
    """删除库存项（需要有效员工编号）"""
    try:
        from services.inventory_service import InventoryService
        inventory_service = InventoryService()
        result = inventory_service.delete_item(item_id)
        if not result:
            raise HTTPException(status_code=404, detail="库存项不存在")
        return {"status": "success", "message": "库存项删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除库存项失败: {str(e)}")


@router.post("/{item_id}/adjust")
async def adjust_stock(item_id: int, delta: float, employee_id: str = Depends(verify_employee_id)):
    """调整库存数量（增加为正，减少为负；需要有效员工编号）"""
    try:
        from services.inventory_service import InventoryService
        inventory_service = InventoryService()
        result = inventory_service.adjust_stock(item_id, delta)
        if not result:
            raise HTTPException(status_code=404, detail="库存项不存在")
        return {"status": "success", "message": "库存数量已调整"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"调整库存失败: {str(e)}")
