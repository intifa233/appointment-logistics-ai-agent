from typing import List, Dict, Any, Optional
from datetime import datetime
from ..base.interfaces import BaseInventoryRepository
from ..base.session_manager import SessionManager
from ..models import TeaInventoryItem


class InventoryRepository(BaseInventoryRepository):
    """
    茶叶库存数据访问对象

    职责：
    1. 茶叶库存项的CRUD操作
    2. 库存数量调整
    3. 低库存预警查询
    """

    def __init__(self, session_manager: SessionManager):
        """
        初始化库存数据仓库

        Args:
            session_manager: 会话管理器
        """
        self.session_manager = session_manager

    def add_item(self, name: str, category: Optional[str] = None, unit: Optional[str] = None,
               stock_quantity: float = 0, reorder_threshold: float = 0,
               unit_price: Optional[float] = None) -> int:
        """添加库存项"""
        with self.session_manager.session_scope() as session:
            item = TeaInventoryItem(
                name=name,
                category=category,
                unit=unit,
                stock_quantity=stock_quantity,
                reorder_threshold=reorder_threshold,
                unit_price=unit_price
            )
            session.add(item)
            session.flush()
            return item.id

    def get_item_by_id(self, item_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取库存项"""
        with self.session_manager.session_scope() as session:
            item = session.query(TeaInventoryItem).filter(TeaInventoryItem.id == item_id).first()
            if not item:
                return None
            return self._item_to_dict(item)

    def get_all_items(self) -> List[Dict[str, Any]]:
        """获取所有库存项"""
        with self.session_manager.session_scope() as session:
            items = session.query(TeaInventoryItem).all()
            return [self._item_to_dict(item) for item in items]

    def update_item(self, item_id: int, **updates) -> bool:
        """更新库存项信息"""
        with self.session_manager.session_scope() as session:
            item = session.query(TeaInventoryItem).filter(TeaInventoryItem.id == item_id).first()
            if not item:
                return False
            for key, value in updates.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            item.updated_at = datetime.utcnow()
            return True

    def delete_item(self, item_id: int) -> bool:
        """删除库存项"""
        with self.session_manager.session_scope() as session:
            item = session.query(TeaInventoryItem).filter(TeaInventoryItem.id == item_id).first()
            if not item:
                return False
            session.delete(item)
            return True

    def adjust_stock(self, item_id: int, delta: float) -> bool:
        """调整库存数量（增加为正，减少为负）"""
        with self.session_manager.session_scope() as session:
            item = session.query(TeaInventoryItem).filter(TeaInventoryItem.id == item_id).first()
            if not item:
                return False
            item.stock_quantity = (item.stock_quantity or 0) + delta
            item.updated_at = datetime.utcnow()
            return True

    def get_low_stock_items(self) -> List[Dict[str, Any]]:
        """获取库存低于补货阈值的项目"""
        with self.session_manager.session_scope() as session:
            items = session.query(TeaInventoryItem).filter(
                TeaInventoryItem.stock_quantity <= TeaInventoryItem.reorder_threshold
            ).all()
            return [self._item_to_dict(item) for item in items]

    def _item_to_dict(self, item: TeaInventoryItem) -> Dict[str, Any]:
        """将库存项对象转换为字典"""
        return {
            'id': item.id,
            'name': item.name,
            'category': item.category,
            'unit': item.unit,
            'stock_quantity': item.stock_quantity,
            'reorder_threshold': item.reorder_threshold,
            'unit_price': item.unit_price,
            'updated_at': item.updated_at
        }
