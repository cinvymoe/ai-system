"""
Camera Mapper

负责将消息数据映射到对应的摄像头列表。
"""

import logging
from typing import Any, Callable, Dict, List, Optional
from sqlalchemy.orm import Session

from .models import CameraInfo
from .errors import CameraMappingError, ErrorHandler

logger = logging.getLogger(__name__)


class CameraMapper:
    """
    摄像头映射器
    
    将消息数据（方向、角度、AI 报警）映射到对应的摄像头列表。
    """
    
    # 方向映射：将系统方向命令映射到数据库存储的方向值
    DIRECTION_MAPPING = {
        'turn_left': ['turn_left', 'left'],      # turn_left 可以匹配 turn_left 或 left
        'turn_right': ['turn_right', 'right'],   # turn_right 可以匹配 turn_right 或 right
        'forward': ['forward'],
        'backward': ['backward'],
        'stationary': ['stationary'],
    }
    
    def __init__(
        self, 
        db_session_factory: Callable[[], Session],
        error_handler: Optional[ErrorHandler] = None
    ):
        """
        初始化摄像头映射器
        
        Args:
            db_session_factory: 数据库会话工厂函数（返回 Session 对象）
            error_handler: 错误处理器（可选）
        """
        self._db_session_factory = db_session_factory
        self._error_handler = error_handler or ErrorHandler(logger)
        logger.info("CameraMapper initialized")
    
    def _get_session(self) -> Session:
        """
        获取数据库会话
        
        处理工厂函数可能是生成器的情况
        
        Returns:
            Session: 数据库会话对象
        """
        session = self._db_session_factory()
        # 如果是生成器，获取第一个值
        if hasattr(session, '__next__'):
            session = next(session)
        return session
    
    def get_cameras_by_direction(
        self, 
        direction: str
    ) -> List[CameraInfo]:
        """
        根据方向获取摄像头列表
        
        使用 ErrorHandler 处理数据库错误，支持重试和降级处理。
        支持方向映射：turn_left 可以匹配 left，turn_right 可以匹配 right
        
        Args:
            direction: 方向命令 (forward, backward, turn_left, turn_right, stationary)
            
        Returns:
            List[CameraInfo]: 摄像头信息列表
        """
        def _query_cameras():
            """内部查询函数，用于重试"""
            # 导入模型（延迟导入避免循环依赖）
            try:
                from models.camera import Camera
            except ImportError:
                from src.models.camera import Camera
            
            db = self._get_session()
            
            try:
                # 获取可能的方向值（支持映射）
                possible_directions = self.DIRECTION_MAPPING.get(
                    direction, 
                    [direction]  # 如果没有映射，使用原始值
                )
                
                # 查询 directions 字段包含该方向的摄像头
                # Camera.directions 是 JSON 数组，需要使用 JSON 查询
                cameras = db.query(Camera).filter(
                    Camera.enabled == True
                ).all()
                
                # 过滤包含指定方向的摄像头（支持多个可能的方向值）
                matching_cameras = []
                for camera in cameras:
                    if camera.directions:
                        # 检查摄像头的方向是否匹配任何可能的方向值
                        for cam_direction in camera.directions:
                            if cam_direction in possible_directions:
                                matching_cameras.append(
                                    CameraInfo(
                                        id=camera.id,
                                        name=camera.name,
                                        url=camera.url,
                                        status=camera.status,
                                        directions=camera.directions
                                    )
                                )
                                break  # 找到匹配就跳出，避免重复添加
                
                logger.info(
                    f"Found {len(matching_cameras)} cameras for direction '{direction}' "
                    f"(searched for: {possible_directions})"
                )
                
                return matching_cameras
                
            finally:
                db.close()
        
        try:
            return _query_cameras()
        except Exception as e:
            # 使用 ErrorHandler 处理数据库错误（带重试）
            result = self._error_handler.handle_database_error(
                operation=_query_cameras,
                operation_name=f"get_cameras_by_direction({direction})",
                error=e
            )
            
            # 如果重试失败，返回空列表（降级处理）
            if result is None:
                logger.warning(
                    f"Returning empty camera list for direction '{direction}' "
                    "after all retries failed"
                )
                return []
            
            return result
    
    def get_cameras_by_angle(
        self, 
        angle: float
    ) -> List[CameraInfo]:
        """
        根据角度获取摄像头列表
        
        使用 ErrorHandler 处理数据库错误，支持重试和降级处理。
        
        Args:
            angle: 角度值
            
        Returns:
            List[CameraInfo]: 摄像头信息列表
        """
        def _query_cameras():
            """内部查询函数，用于重试"""
            # 导入模型（延迟导入避免循环依赖）
            try:
                from models.angle_range import AngleRange
                from models.camera import Camera
            except ImportError:
                from src.models.angle_range import AngleRange
                from src.models.camera import Camera
            
            db = self._get_session()
            
            try:
                # 查询包含该角度的角度范围
                angle_ranges = db.query(AngleRange).filter(
                    AngleRange.enabled == True,
                    AngleRange.min_angle <= angle,
                    AngleRange.max_angle >= angle
                ).all()
                
                # 收集所有关联的摄像头 ID
                camera_ids = set()
                for angle_range in angle_ranges:
                    if angle_range.camera_ids:
                        camera_ids.update(angle_range.camera_ids)
                
                # 查询摄像头详情
                cameras = []
                if camera_ids:
                    camera_objects = db.query(Camera).filter(
                        Camera.id.in_(camera_ids),
                        Camera.enabled == True
                    ).all()
                    
                    for camera in camera_objects:
                        cameras.append(
                            CameraInfo(
                                id=camera.id,
                                name=camera.name,
                                url=camera.url,
                                status=camera.status,
                                directions=camera.directions or []
                            )
                        )
                
                logger.info(
                    f"Found {len(cameras)} cameras for angle {angle}° "
                    f"(matched {len(angle_ranges)} angle ranges)"
                )
                
                return cameras
                
            finally:
                db.close()
        
        try:
            return _query_cameras()
        except Exception as e:
            # 使用 ErrorHandler 处理数据库错误（带重试）
            result = self._error_handler.handle_database_error(
                operation=_query_cameras,
                operation_name=f"get_cameras_by_angle({angle})",
                error=e
            )
            
            # 如果重试失败，返回空列表（降级处理）
            if result is None:
                logger.warning(
                    f"Returning empty camera list for angle {angle}° "
                    "after all retries failed"
                )
                return []
            
            return result
    
    def get_cameras_by_ai_alert(
        self, 
        alert_data: Dict[str, Any]
    ) -> List[CameraInfo]:
        """
        根据 AI 报警获取摄像头列表（预留接口）
        
        Args:
            alert_data: AI 报警数据
            
        Returns:
            List[CameraInfo]: 摄像头信息列表（当前返回空列表）
        """
        logger.info(
            f"AI alert camera mapping called (placeholder): {alert_data.get('alert_type')}"
        )
        
        # 预留实现：未来可以根据报警类型、位置等信息查询相关摄像头
        # 当前返回空列表
        return []
    
    def get_all_direction_mappings(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取所有方向的摄像头映射
        
        Returns:
            Dict[str, List[Dict]]: 方向到摄像头列表的映射
        """
        directions = ['forward', 'backward', 'turn_left', 'turn_right', 'stationary']
        mappings = {}
        
        for direction in directions:
            try:
                cameras = self.get_cameras_by_direction(direction)
                mappings[direction] = [cam.to_dict() for cam in cameras]
            except Exception as e:
                logger.error(f"Failed to get mapping for direction {direction}: {e}")
                mappings[direction] = []
        
        return mappings
    
    def get_all_angle_ranges(self) -> List[Dict[str, Any]]:
        """
        获取所有角度范围及其关联的摄像头
        
        使用 ErrorHandler 处理数据库错误。
        
        Returns:
            List[Dict]: 角度范围列表
        """
        def _query_angle_ranges():
            """内部查询函数，用于重试"""
            # 导入模型
            try:
                from models.angle_range import AngleRange
            except ImportError:
                from src.models.angle_range import AngleRange
            
            db = self._get_session()
            
            try:
                angle_ranges = db.query(AngleRange).filter(
                    AngleRange.enabled == True
                ).all()
                
                result = []
                for angle_range in angle_ranges:
                    # 获取该范围的摄像头
                    cameras = self.get_cameras_by_angle(
                        (angle_range.min_angle + angle_range.max_angle) / 2
                    )
                    
                    result.append({
                        'id': angle_range.id,
                        'name': angle_range.name,
                        'min_angle': angle_range.min_angle,
                        'max_angle': angle_range.max_angle,
                        'cameras': [cam.to_dict() for cam in cameras]
                    })
                
                return result
                
            finally:
                db.close()
        
        try:
            return _query_angle_ranges()
        except Exception as e:
            # 使用 ErrorHandler 处理数据库错误（带重试）
            result = self._error_handler.handle_database_error(
                operation=_query_angle_ranges,
                operation_name="get_all_angle_ranges",
                error=e
            )
            
            # 如果重试失败，返回空列表（降级处理）
            if result is None:
                logger.warning(
                    "Returning empty angle ranges list after all retries failed"
                )
                return []
            
            return result
