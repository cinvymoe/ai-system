"""AI Settings SQLAlchemy ORM model."""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float, JSON
from datetime import datetime

try:
    from database import Base
except ImportError:
    from src.database import Base


class AISettings(Base):
    """AI Settings model for AI recognition configuration."""
    
    __tablename__ = "ai_settings"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 启用状态
    enabled = Column(Boolean, default=True)  # 是否启用AI检测
    
    # 摄像头绑定
    camera_id = Column(String, nullable=True)  # 绑定的摄像头ID
    camera_name = Column(String, nullable=True)  # 摄像头名称（冗余字段，便于查询）
    camera_url = Column(String, nullable=True)  # 摄像头URL（冗余字段）
    
    # 检测参数
    confidence_threshold = Column(Float, default=75.0)  # 置信度阈值 (0-100)
    
    # 危险区域 (4个点的坐标，存储为JSON)
    # 格式: [{"x": 0.1, "y": 0.2}, {"x": 0.3, "y": 0.2}, {"x": 0.3, "y": 0.8}, {"x": 0.1, "y": 0.8}]
    danger_zone = Column(JSON, nullable=True)  # 危险区域的4个点
    
    # 警告区域 (4个点的坐标，存储为JSON)
    warning_zone = Column(JSON, nullable=True)  # 警告区域的4个点
    
    # 报警设置
    sound_alarm = Column(Boolean, default=True)  # 声音报警
    visual_alarm = Column(Boolean, default=True)  # 视觉报警
    auto_screenshot = Column(Boolean, default=True)  # 自动截图
    alarm_cooldown = Column(Integer, default=5)  # 报警冷却时间（秒）
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Table configuration
    __table_args__ = {'extend_existing': True}
    
    def __repr__(self):
        return f"<AISettings(id={self.id}, camera_id={self.camera_id}, confidence={self.confidence_threshold})>"
