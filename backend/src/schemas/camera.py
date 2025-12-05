"""Pydantic schemas for camera data validation."""
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Literal, Optional, List
from datetime import datetime


class CameraBase(BaseModel):
    """Base camera schema with common fields."""
    
    name: str = Field(..., min_length=1, max_length=100, description="摄像头名称")
    address: str = Field(..., description="摄像头IP地址，如：192.168.1.254")
    username: str = Field(..., description="摄像头用户名")
    password: str = Field(..., description="摄像头密码")
    channel: int = Field(default=1, ge=1, le=999, description="通道号")
    directions: List[Literal["forward", "backward", "left", "right", "idle"]] = Field(
        default=["forward"], 
        description="摄像头方向，可多选"
    )
    stream_type: Literal["main", "sub"] = Field(default="main", description="码流类型：main=主码流(01), sub=子码流(02)")
    enabled: bool = Field(default=True, description="是否启用")
    url: Optional[str] = Field(None, description="RTSP URL，自动生成")
    resolution: str = "1920x1080"
    fps: int = Field(default=30, ge=1, le=60)
    brightness: int = Field(default=50, ge=0, le=100)
    contrast: int = Field(default=50, ge=0, le=100)
    status: Literal["online", "offline"] = "offline"
    
    @model_validator(mode='after')
    def generate_url(self):
        """根据配置自动生成RTSP URL"""
        # 根据码流类型确定通道号后缀：主码流=01，子码流=02
        stream_suffix = "01" if self.stream_type == "main" else "02"
        # 生成完整的通道号：通道号 + 码流后缀（如：1 -> 101, 2 -> 202）
        full_channel = f"{self.channel}{stream_suffix}"
        # 生成RTSP URL
        self.url = f"rtsp://{self.username}:{self.password}@{self.address}/Streaming/Channels/{full_channel}"
        return self
    
    @field_validator('resolution')
    @classmethod
    def validate_resolution(cls, v: str) -> str:
        """Validate resolution format (e.g., '1920x1080')."""
        if not v or 'x' not in v:
            raise ValueError('Invalid resolution format. Expected format: WIDTHxHEIGHT (e.g., 1920x1080)')
        
        parts = v.split('x')
        if len(parts) != 2:
            raise ValueError('Invalid resolution format. Expected format: WIDTHxHEIGHT (e.g., 1920x1080)')
        
        try:
            width = int(parts[0])
            height = int(parts[1])
            if width <= 0 or height <= 0:
                raise ValueError('Resolution width and height must be positive integers')
        except ValueError as e:
            if 'invalid literal' in str(e):
                raise ValueError('Resolution width and height must be valid integers')
            raise
        
        return v


class CameraCreate(CameraBase):
    """Schema for creating a new camera."""
    pass


class CameraUpdate(BaseModel):
    """Schema for updating an existing camera. All fields are optional."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="摄像头名称")
    address: Optional[str] = Field(None, description="摄像头IP地址")
    username: Optional[str] = Field(None, description="摄像头用户名")
    password: Optional[str] = Field(None, description="摄像头密码")
    channel: Optional[int] = Field(None, ge=1, le=999, description="通道号")
    directions: Optional[List[Literal["forward", "backward", "left", "right", "idle"]]] = Field(
        None, 
        description="摄像头方向，可多选"
    )
    stream_type: Optional[Literal["main", "sub"]] = Field(None, description="码流类型：main=主码流, sub=子码流")
    enabled: Optional[bool] = Field(None, description="是否启用")
    url: Optional[str] = None
    resolution: Optional[str] = None
    fps: Optional[int] = Field(None, ge=1, le=60)
    brightness: Optional[int] = Field(None, ge=0, le=100)
    contrast: Optional[int] = Field(None, ge=0, le=100)
    status: Optional[Literal["online", "offline"]] = None
    
    @model_validator(mode='after')
    def generate_url_if_needed(self):
        """如果提供了地址、用户名、密码等信息，自动生成URL"""
        # 检查是否有足够的信息生成URL
        if self.address and self.username and self.password:
            # 使用提供的值或默认值
            channel = self.channel if self.channel is not None else 1
            stream_type = self.stream_type if self.stream_type is not None else "main"
            
            # 根据码流类型确定通道号后缀
            stream_suffix = "01" if stream_type == "main" else "02"
            full_channel = f"{channel}{stream_suffix}"
            
            # 生成RTSP URL
            self.url = f"rtsp://{self.username}:{self.password}@{self.address}/Streaming/Channels/{full_channel}"
        
        return self
    
    @field_validator('resolution')
    @classmethod
    def validate_resolution(cls, v: Optional[str]) -> Optional[str]:
        """Validate resolution format if provided."""
        if v is None:
            return v
        
        if not v or 'x' not in v:
            raise ValueError('Invalid resolution format. Expected format: WIDTHxHEIGHT (e.g., 1920x1080)')
        
        parts = v.split('x')
        if len(parts) != 2:
            raise ValueError('Invalid resolution format. Expected format: WIDTHxHEIGHT (e.g., 1920x1080)')
        
        try:
            width = int(parts[0])
            height = int(parts[1])
            if width <= 0 or height <= 0:
                raise ValueError('Resolution width and height must be positive integers')
        except ValueError as e:
            if 'invalid literal' in str(e):
                raise ValueError('Resolution width and height must be valid integers')
            raise
        
        return v


class CameraResponse(CameraBase):
    """Schema for camera response with additional fields."""
    
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
