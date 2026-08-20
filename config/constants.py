from enum import Enum
tea_master_busy_periods_dict = {}  # { tea_master_id: [ {"start": "...", "end": "..."} ] }
room_busy_periods_dict = {}  # { room_id: [ {"start": "...", "end": "..."} ] }

# 允许编辑茶叶库存的员工编号（CC001 - CC010）
AUTHORIZED_INVENTORY_EDITOR_IDS = {f"CC{i:03d}" for i in range(1, 11)}

class StateEnum(Enum):
    CLASSIFY = "classify"
    APPOINTMENT = "appointment"
    CONSULT = "consult"
    OTHER = "other"

class SharedState:
    def __init__(self):
        self.value = StateEnum.CLASSIFY
