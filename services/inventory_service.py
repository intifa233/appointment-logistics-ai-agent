# services/inventory_service.py

from typing import List, Dict, Any, Optional
from db.db_router import DatabaseRouter
import logging

logger = logging.getLogger(__name__)

class InventoryService:
    """茶叶库存服务类 - 管理茶叶库存数据和默认初始化"""

    def __init__(self):
        self.db = DatabaseRouter()

        # 默认库存数据（10种常见茶叶）
        self.default_items = [
            {"name": "西湖龙井", "category": "绿茶", "unit": "克", "stock_quantity": 3000, "reorder_threshold": 500, "unit_price": 2.8},
            {"name": "铁观音", "category": "乌龙茶", "unit": "克", "stock_quantity": 4000, "reorder_threshold": 600, "unit_price": 1.8},
            {"name": "普洱生茶", "category": "普洱", "unit": "克", "stock_quantity": 5000, "reorder_threshold": 800, "unit_price": 1.5},
            {"name": "普洱熟茶", "category": "普洱", "unit": "克", "stock_quantity": 5000, "reorder_threshold": 800, "unit_price": 1.2},
            {"name": "茉莉花茶", "category": "花茶", "unit": "克", "stock_quantity": 3500, "reorder_threshold": 500, "unit_price": 1.0},
            {"name": "大红袍", "category": "乌龙茶", "unit": "克", "stock_quantity": 2000, "reorder_threshold": 400, "unit_price": 4.5},
            {"name": "白毫银针", "category": "白茶", "unit": "克", "stock_quantity": 1500, "reorder_threshold": 300, "unit_price": 6.0},
            {"name": "太平猴魁", "category": "绿茶", "unit": "克", "stock_quantity": 1800, "reorder_threshold": 300, "unit_price": 3.5},
            {"name": "蜜香红茶", "category": "红茶", "unit": "克", "stock_quantity": 2500, "reorder_threshold": 400, "unit_price": 2.2},
            {"name": "抹茶粉", "category": "绿茶", "unit": "克", "stock_quantity": 1200, "reorder_threshold": 300, "unit_price": 5.0}
        ]

    def initialize_default_items(self) -> bool:
        """初始化默认库存数据"""
        try:
            existing_items = self.db.inventory.get_all_items()

            if existing_items:
                logger.info(f"数据库中已有 {len(existing_items)} 种茶叶库存，跳过初始化")
                return True

            logger.info("数据库中无库存数据，开始初始化默认茶叶库存")

            for item_data in self.default_items:
                try:
                    item_id = self.db.inventory.add_item(
                        name=item_data['name'],
                        category=item_data['category'],
                        unit=item_data['unit'],
                        stock_quantity=item_data['stock_quantity'],
                        reorder_threshold=item_data['reorder_threshold'],
                        unit_price=item_data['unit_price']
                    )
                    logger.debug(f"添加库存项: {item_data['name']} (ID: {item_id})")

                except Exception as e:
                    logger.error(f"添加库存项 {item_data['name']} 失败: {e}")
                    return False

            final_count = len(self.db.inventory.get_all_items())
            logger.info(f"库存初始化完成，共添加 {final_count} 种茶叶")
            return True

        except Exception as e:
            logger.error(f"库存初始化失败: {e}")
            return False

    def get_all_items(self) -> List[Dict[str, Any]]:
        """获取所有库存项"""
        return self.db.inventory.get_all_items()

    def get_item_by_id(self, item_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取库存项"""
        return self.db.inventory.get_item_by_id(item_id)

    def add_item(self, name: str, category: str = None, unit: str = None,
               stock_quantity: float = 0, reorder_threshold: float = 0,
               unit_price: float = None) -> int:
        """添加库存项"""
        return self.db.inventory.add_item(name, category, unit, stock_quantity, reorder_threshold, unit_price)

    def update_item(self, item_id: int, **updates) -> bool:
        """更新库存项"""
        return self.db.inventory.update_item(item_id, **updates)

    def delete_item(self, item_id: int) -> bool:
        """删除库存项"""
        return self.db.inventory.delete_item(item_id)

    def adjust_stock(self, item_id: int, delta: float) -> bool:
        """调整库存数量（增加为正，减少为负）"""
        return self.db.inventory.adjust_stock(item_id, delta)

    def get_low_stock_items(self) -> List[Dict[str, Any]]:
        """获取库存低于补货阈值的项目"""
        return self.db.inventory.get_low_stock_items()
