"""Angle Range SQLAlchemy ORM model."""
from sqlalchemy import Column, String, Integer, Boolean, JSON, DateTime
from datetime import datetime

try:
    from database import Base
except ImportError:
    from src.database import Base


class AngleRange(Base):
    """Angle range model for defining custom angle ranges and binding cameras."""
    
    __tablename__ = "angle_ranges"
    
    # Primary key
    id = Column(String, primary_key=True)
    
    # Angle range definition
    name = Column(String, nullable=False, unique=True)  # 角度范围名称，如"30-90度"
    min_angle = Column(Integer, nullable=False)  # 最小角度
    max_angle = Column(Integer, nullable=False)  # 最大角度
    enabled = Column(Boolean, default=True)  # 是否启用
    
    # Bound cameras (存储为JSON数组，包含摄像头ID列表)
    camera_ids = Column(JSON, nullable=False, default=[])
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Table configuration
    __table_args__ = {'extend_existing': True}
    
    def __repr__(self):
        return f"<AngleRange(id={self.id}, name={self.name}, range={self.min_angle}-{self.max_angle}, enabled={self.enabled}, cameras={len(self.camera_ids)})>"
