"""AI Settings API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

try:
    from database import get_db
    from schemas.ai_settings import AISettingsCreate, AISettingsUpdate, AISettingsResponse
    from services.ai_settings_service import AISettingsService
except ImportError:
    from src.database import get_db
    from src.schemas.ai_settings import AISettingsCreate, AISettingsUpdate, AISettingsResponse
    from src.services.ai_settings_service import AISettingsService

router = APIRouter(prefix="/api/ai-settings", tags=["AI Settings"])


@router.get("", response_model=AISettingsResponse)
def get_ai_settings(db: Session = Depends(get_db)):
    """
    获取AI识别设置
    
    如果不存在设置，会自动创建默认设置
    """
    service = AISettingsService(db)
    settings = service.get_settings()
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI设置不存在"
        )
    return settings


@router.post("", response_model=AISettingsResponse, status_code=status.HTTP_201_CREATED)
def create_ai_settings(
    settings_data: AISettingsCreate,
    db: Session = Depends(get_db)
):
    """
    创建AI识别设置
    
    - **camera_id**: 绑定的摄像头ID（可选）
    - **confidence_threshold**: 置信度阈值 (0-100)
    - **danger_zone**: 危险区域的4个点坐标
    - **warning_zone**: 警告区域的4个点坐标
    - **sound_alarm**: 是否启用声音报警
    - **visual_alarm**: 是否启用视觉报警
    - **auto_screenshot**: 是否自动截图
    - **alarm_cooldown**: 报警冷却时间（秒）
    """
    try:
        service = AISettingsService(db)
        return service.create_settings(settings_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{settings_id}", response_model=AISettingsResponse)
def update_ai_settings(
    settings_id: int,
    settings_data: AISettingsUpdate,
    db: Session = Depends(get_db)
):
    """
    更新AI识别设置
    
    所有字段都是可选的，只更新提供的字段
    """
    try:
        service = AISettingsService(db)
        settings = service.update_settings(settings_id, settings_data)
        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"AI设置 {settings_id} 不存在"
            )
        return settings
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{settings_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ai_settings(
    settings_id: int,
    db: Session = Depends(get_db)
):
    """
    删除AI识别设置
    """
    service = AISettingsService(db)
    success = service.delete_settings(settings_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI设置 {settings_id} 不存在"
        )


@router.post("/{settings_id}/bind-camera/{camera_id}", response_model=AISettingsResponse)
def bind_camera_to_ai_settings(
    settings_id: int,
    camera_id: str,
    db: Session = Depends(get_db)
):
    """
    绑定摄像头到AI设置
    
    - **settings_id**: AI设置ID
    - **camera_id**: 要绑定的摄像头ID
    """
    try:
        service = AISettingsService(db)
        settings = service.bind_camera(settings_id, camera_id)
        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"AI设置 {settings_id} 不存在"
            )
        return settings
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{settings_id}/unbind-camera", response_model=AISettingsResponse)
def unbind_camera_from_ai_settings(
    settings_id: int,
    db: Session = Depends(get_db)
):
    """
    解绑摄像头
    
    - **settings_id**: AI设置ID
    """
    service = AISettingsService(db)
    settings = service.unbind_camera(settings_id)
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI设置 {settings_id} 不存在"
        )
    return settings
