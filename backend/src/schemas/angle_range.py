"""Pydantic schemas for angle range data validation."""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime


class AngleRangeBase(BaseModel):
    """Base angle range schema with common fields."""
    
    name: str = Field(..., min_length=1, max_length=100, description="角度范围名称")
    min_angle: int = Field(..., ge=0, le=360, description="最小角度 (0-360)")
    max_angle: int = Field(..., ge=0, le=360, description="最大角度 (0-360)")
    enabled: bool = Field(default=True, description="是否启用")
    camera_ids: List[str] = Field(default=[], description="绑定的摄像头ID列表")
    
    @field_validator('max_angle')
    @classmethod
    def validate_angle_range(cls, v: int, info) -> int:
        """Validate that max_angle is greater than min_angle."""
        min_angle = info.data.get('min_angle')
        if min_angle is not None and v <= min_angle:
            raise ValueError('max_angle must be greater than min_angle')
        return v


class AngleRangeCreate(AngleRangeBase):
    """Schema for creating a new angle range."""
    pass


class AngleRangeUpdate(BaseModel):
    """Schema for updating an existing angle range. All fields are optional."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="角度范围名称")
    min_angle: Optional[int] = Field(None, ge=0, le=360, description="最小角度 (0-360)")
    max_angle: Optional[int] = Field(None, ge=0, le=360, description="最大角度 (0-360)")
    enabled: Optional[bool] = Field(None, description="是否启用")
    camera_ids: Optional[List[str]] = Field(None, description="绑定的摄像头ID列表")


class AngleRangeResponse(AngleRangeBase):
    """Schema for angle range response with additional fields."""
    
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
