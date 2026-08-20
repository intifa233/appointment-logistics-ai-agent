from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class TeaMaster(Base):
    __tablename__ = 'tea_masters'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    gender = Column(String, nullable=True)      # 性别字段
    specialty = Column(String, nullable=True)   # 茶艺专长字段（如：功夫茶艺、普洱鉴赏）
    schedules = relationship("TeaMasterSchedule", back_populates="tea_master", cascade="all, delete-orphan")

class TeaMasterSchedule(Base):
    __tablename__ = 'tea_master_schedules'
    id = Column(Integer, primary_key=True)
    tea_master_id = Column(Integer, ForeignKey('tea_masters.id'))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)  # 'busy' or 'free'
    appointment_id = Column(Integer, nullable=True)
    tea_master = relationship("TeaMaster", back_populates="schedules")

class TeaRoom(Base):
    __tablename__ = 'tea_rooms'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    room_type = Column(String, nullable=True)   # 雅座 / 包间 / 茶道体验室
    capacity = Column(Integer, nullable=True)    # 可容纳人数
    equipment = Column(JSON, nullable=True)      # 设备清单，如 ["茶具", "香炉"]
    status = Column(String, default='available')  # 'available' or 'maintenance'
    schedules = relationship("TeaRoomSchedule", back_populates="room", cascade="all, delete-orphan")

class TeaRoomSchedule(Base):
    __tablename__ = 'tea_room_schedules'
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('tea_rooms.id'))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)  # 'busy' or 'free'
    appointment_id = Column(Integer, nullable=True)
    room = relationship("TeaRoom", back_populates="schedules")

class TeaInventoryItem(Base):
    __tablename__ = 'tea_inventory_items'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    category = Column(String, nullable=True)     # 绿茶 / 乌龙 / 普洱 / 花茶 / 红茶 / 黑茶
    unit = Column(String, nullable=True)          # 克 / 盒 / 罐
    stock_quantity = Column(Float, default=0)
    reorder_threshold = Column(Float, default=0)  # 低于此值提示补货
    unit_price = Column(Float, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class KnowledgeDocument(Base):
    __tablename__ = 'knowledge_documents'
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    keywords = Column(JSON, nullable=True)  # 存储关键词列表
    embedding = Column(JSON, nullable=True)  # 存储嵌入向量
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Integer, default=1)  # 软删除标记

class UserBehavior(Base):
    __tablename__ = 'user_behaviors'
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False, default='default_user')  # 单用户场景使用默认用户ID
    action_type = Column(String, nullable=False)  # 'appointment', 'consultation', 'inquiry'
    action_data = Column(JSON, nullable=True)  # 存储行为相关的详细数据
    tea_master_id = Column(Integer, ForeignKey('tea_masters.id'), nullable=True)
    session_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    tea_master = relationship("TeaMaster")

class UserPreference(Base):
    __tablename__ = 'user_preferences'
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False, default='default_user')
    preference_type = Column(String, nullable=False)  # 'tea_master', 'time', 'service', 'duration'
    preference_value = Column(String, nullable=False)
    confidence_score = Column(Integer, default=1)  # 偏好的置信度（出现次数）
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserRecommendation(Base):
    __tablename__ = 'user_recommendations'
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False, default='default_user')
    recommendation_type = Column(String, nullable=False)  # 'tea_master_available', 'return_reminder', 'service_suggestion'
    content = Column(Text, nullable=False)
    tea_master_id = Column(Integer, ForeignKey('tea_masters.id'), nullable=True)
    is_sent = Column(Integer, default=0)  # 是否已发送
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    tea_master = relationship("TeaMaster")
