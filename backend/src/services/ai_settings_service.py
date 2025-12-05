"""AI Settings service for business logic."""
from sqlalchemy.orm import Session
from typing import Optional

try:
    from repositories.ai_settings_repository import AISettingsRepository
    from schemas.ai_settings import AISettingsCreate, AISettingsUpdate, AISettingsResponse
    from models.ai_settings import AISettings
except ImportError:
    from src.repositories.ai_settings_repository import AISettingsRepository
    from src.schemas.ai_settings import AISettingsCreate, AISettingsUpdate, AISettingsResponse
    from src.models.ai_settings import AISettings


class AISettingsService:
    """Service for AI Settings business logic."""
    
    def __init__(self, db: Session):
        self.repository = AISettingsRepository(db)
        self.db = db
    
    def get_settings(self) -> Optional[AISettingsResponse]:
        """获取AI设置"""
        settings = self.repository.get_or_create_default()
        if settings:
            return AISettingsResponse.model_validate(settings)
        return None
    
    def create_settings(self, settings_data: AISettingsCreate) -> AISettingsResponse:
        """创建AI设置"""
        # 验证区域点数量
        if settings_data.danger_zone and len(settings_data.danger_zone) != 4:
            raise ValueError("危险区域必须包含4个点")
        if settings_data.warning_zone and len(settings_data.warning_zone) != 4:
            raise ValueError("警告区域必须包含4个点")
        
        # 如果提供了camera_id，验证摄像头是否存在
        if settings_data.camera_id:
            from src.repositories.camera_repository import CameraRepository
            camera_repo = CameraRepository(self.db)
            camera = camera_repo.get_by_id(settings_data.camera_id)
            if not camera:
                raise ValueError(f"摄像头 {settings_data.camera_id} 不存在")
            # 自动填充摄像头信息
            settings_data.camera_name = camera.name
            settings_data.camera_url = camera.url
        
        settings = self.repository.create(settings_data)
        return AISettingsResponse.model_validate(settings)
    
    def update_settings(self, settings_id: int, settings_data: AISettingsUpdate) -> Optional[AISettingsResponse]:
        """更新AI设置"""
        # 验证区域点数量
        if settings_data.danger_zone is not None and len(settings_data.danger_zone) != 4:
            raise ValueError("危险区域必须包含4个点")
        if settings_data.warning_zone is not None and len(settings_data.warning_zone) != 4:
            raise ValueError("警告区域必须包含4个点")
        
        # 如果更新了camera_id，验证摄像头是否存在并更新相关信息
        if settings_data.camera_id:
            from src.repositories.camera_repository import CameraRepository
            camera_repo = CameraRepository(self.db)
            camera = camera_repo.get_by_id(settings_data.camera_id)
            if not camera:
                raise ValueError(f"摄像头 {settings_data.camera_id} 不存在")
            # 自动更新摄像头信息
            settings_data.camera_name = camera.name
            settings_data.camera_url = camera.url
        
        settings = self.repository.update(settings_id, settings_data)
        if settings:
            return AISettingsResponse.model_validate(settings)
        return None
    
    def delete_settings(self, settings_id: int) -> bool:
        """删除AI设置"""
        return self.repository.delete(settings_id)
    
    def bind_camera(self, settings_id: int, camera_id: str) -> Optional[AISettingsResponse]:
        """绑定摄像头到AI设置"""
        from src.repositories.camera_repository import CameraRepository
        camera_repo = CameraRepository(self.db)
        camera = camera_repo.get_by_id(camera_id)
        
        if not camera:
            raise ValueError(f"摄像头 {camera_id} 不存在")
        
        update_data = AISettingsUpdate(
            camera_id=camera_id,
            camera_name=camera.name,
            camera_url=camera.url
        )
        
        return self.update_settings(settings_id, update_data)
    
    def unbind_camera(self, settings_id: int) -> Optional[AISettingsResponse]:
        """解绑摄像头"""
        update_data = AISettingsUpdate(
            camera_id=None,
            camera_name=None,
            camera_url=None
        )
        
        return self.update_settings(settings_id, update_data)
