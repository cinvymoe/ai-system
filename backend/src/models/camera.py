"""Camera SQLAlchemy ORM model."""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Index, JSON
from datetime import datetime

try:
    from database import Base
except ImportError:
    from src.database import Base


class Camera(Base):
    """Camera model representing a security camera in the system."""
    
    __tablename__ = "cameras"
    
    # Primary key
    id = Column(String, primary_key=True)
    
    # Basic information
    name = Column(String, nullable=False, unique=True)
    address = Column(String, nullable=False)  # IP地址
    username = Column(String, nullable=False)  # 用户名
    password = Column(String, nullable=False)  # 密码
    channel = Column(Integer, default=1)  # 通道号
    stream_type = Column(String, default="main")  # 码流类型: main/sub
    url = Column(String, nullable=False)  # 自动生成的RTSP URL
    enabled = Column(Boolean, default=True)
    
    # Video settings
    resolution = Column(String, default="1920x1080")
    fps = Column(Integer, default=30)
    brightness = Column(Integer, default=50)
    contrast = Column(Integer, default=50)
    
    # Status and directions (多选，存储为JSON数组)
    status = Column(String, default="offline", index=True)  # 'online' | 'offline'
    directions = Column(JSON, nullable=False, default=["forward"])  # 方向数组，可多选
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Table configuration
    __table_args__ = {'extend_existing': True}
    
    def __repr__(self):
        return f"<Camera(id={self.id}, name={self.name}, directions={self.directions}, status={self.status})>"
