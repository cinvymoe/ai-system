"""API endpoints for angle range management."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import uuid

try:
    from database import get_db
    from models.angle_range import AngleRange
    from schemas.angle_range import AngleRangeCreate, AngleRangeUpdate, AngleRangeResponse
except ImportError:
    from src.database import get_db
    from src.models.angle_range import AngleRange
    from src.schemas.angle_range import AngleRangeCreate, AngleRangeUpdate, AngleRangeResponse

router = APIRouter(prefix="/api/angle-ranges", tags=["angle-ranges"])


@router.get("", response_model=List[AngleRangeResponse])
async def get_all_angle_ranges(db: Session = Depends(get_db)):
    """获取所有角度范围配置"""
    angle_ranges = db.query(AngleRange).all()
    return angle_ranges


@router.get("/{angle_range_id}", response_model=AngleRangeResponse)
async def get_angle_range(angle_range_id: str, db: Session = Depends(get_db)):
    """根据ID获取角度范围配置"""
    angle_range = db.query(AngleRange).filter(AngleRange.id == angle_range_id).first()
    if not angle_range:
        raise HTTPException(status_code=404, detail="Angle range not found")
    return angle_range


@router.post("", response_model=AngleRangeResponse, status_code=201)
async def create_angle_range(angle_range_data: AngleRangeCreate, db: Session = Depends(get_db)):
    """创建新的角度范围配置"""
    # 检查名称是否已存在
    existing = db.query(AngleRange).filter(AngleRange.name == angle_range_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Angle range with name '{angle_range_data.name}' already exists")
    
    # 创建新角度范围
    new_angle_range = AngleRange(
        id=str(uuid.uuid4()),
        **angle_range_data.model_dump()
    )
    
    db.add(new_angle_range)
    db.commit()
    db.refresh(new_angle_range)
    
    return new_angle_range


@router.put("/{angle_range_id}", response_model=AngleRangeResponse)
async def update_angle_range(
    angle_range_id: str,
    angle_range_data: AngleRangeUpdate,
    db: Session = Depends(get_db)
):
    """更新角度范围配置"""
    angle_range = db.query(AngleRange).filter(AngleRange.id == angle_range_id).first()
    if not angle_range:
        raise HTTPException(status_code=404, detail="Angle range not found")
    
    # 如果更新名称，检查是否与其他角度范围冲突
    if angle_range_data.name and angle_range_data.name != angle_range.name:
        existing = db.query(AngleRange).filter(AngleRange.name == angle_range_data.name).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Angle range with name '{angle_range_data.name}' already exists")
    
    # 更新字段
    update_data = angle_range_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(angle_range, field, value)
    
    db.commit()
    db.refresh(angle_range)
    
    return angle_range


@router.delete("/{angle_range_id}", status_code=204)
async def delete_angle_range(angle_range_id: str, db: Session = Depends(get_db)):
    """删除角度范围配置"""
    angle_range = db.query(AngleRange).filter(AngleRange.id == angle_range_id).first()
    if not angle_range:
        raise HTTPException(status_code=404, detail="Angle range not found")
    
    db.delete(angle_range)
    db.commit()
    
    return None
