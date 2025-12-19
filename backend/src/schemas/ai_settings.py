"""AI Settings Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Point(BaseModel):
    """坐标点模型"""
    x: float = Field(..., ge=0, le=1, description="X坐标 (0-1)")
    y: float = Field(..., ge=0, le=1, description="Y坐标 (0-1)")


class AISettingsBase(BaseModel):
    """Base schema for AI Settings"""
    enabled: bool = Field(True, description="是否启用AI检测")
    camera_id: Optional[str] = Field(None, description="绑定的摄像头ID")
    camera_name: Optional[str] = Field(None, description="摄像头名称")
    camera_url: Optional[str] = Field(None, description="摄像头URL")
    confidence_threshold: float = Field(75.0, ge=0, le=100, description="置信度阈值 (0-100)")
    danger_zone: Optional[List[Point]] = Field(None, description="危险区域的4个点")
    warning_zone: Optional[List[Point]] = Field(None, description="警告区域的4个点")
    sound_alarm: bool = Field(True, description="声音报警")
    visual_alarm: bool = Field(True, description="视觉报警")
    auto_screenshot: bool = Field(True, description="自动截图")
    alarm_cooldown: int = Field(5, ge=0, description="报警冷却时间（秒）")


class AISettingsCreate(AISettingsBase):
    """Schema for creating AI Settings"""
    pass


class AISettingsUpdate(BaseModel):
    """Schema for updating AI Settings (all fields optional)"""
    enabled: Optional[bool] = None
    camera_id: Optional[str] = None
    camera_name: Optional[str] = None
    camera_url: Optional[str] = None
    confidence_threshold: Optional[float] = Field(None, ge=0, le=100)
    danger_zone: Optional[List[Point]] = None
    warning_zone: Optional[List[Point]] = None
    sound_alarm: Optional[bool] = None
    visual_alarm: Optional[bool] = None
    auto_screenshot: Optional[bool] = None
    alarm_cooldown: Optional[int] = Field(None, ge=0)


class AISettingsResponse(AISettingsBase):
    """Schema for AI Settings response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
