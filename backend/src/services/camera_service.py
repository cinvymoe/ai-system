"""Camera service for business logic operations."""
import logging
import asyncio
from typing import List, Dict
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import cv2
from urllib.parse import urlparse

from src.repositories.camera_repository import CameraRepository
from src.schemas.camera import CameraCreate, CameraUpdate, CameraResponse

try:
    from config import settings
except ImportError:
    from src.config import settings

# Configure logging
logger = logging.getLogger(__name__)


class CameraService:
   
    
    def __init__(self, repository: CameraRepository):
        """Initialize the service with a camera repository.
        
        Args:
            repository: CameraRepository instance for data access
        """
        self.repository = repository
    
    def get_all_cameras(self) -> List[CameraResponse]:
        """Retrieve all cameras from the database.
        
        Returns:
            List of CameraResponse objects
            
        Raes:
            HTTPException: If database query fails
        """
        try:
            logger.info("Fetching all cameras")
            cameras = self.repository.get_all()
            logger.info(f"Successfully retrieved {len(cameras)} cameras")
            return [CameraResponse.model_validate(cam) for cam in cameras]
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching all cameras: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch cameras from database"
            )
        except Exception as e:
            logger.error(f"Unexpected error while fetching all cameras: {e}")
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred"
            )
    
    def get_camera_by_id(self, camera_id: str) -> CameraResponse:
        """Retrieve a camera by its ID.
        
        Args:
            camera_id: The unique identifier of the camera
            
        Returns:
            CameraResponse object
            
        Raises:
            HTTPException: If camera not found or database error occurs
        """
        try:
            logger.info(f"Fetching camera with ID: {camera_id}")
            camera = self.repository.get_by_id(camera_id)
            
            if not camera:
                logger.warning(f"Camera not found with ID: {camera_id}")
                raise HTTPException(
                    status_code=404,
                    detail=f"Camera with ID '{camera_id}' not found"
                )
            
            logger.info(f"Successfully retrieved camera: {camera.name}")
            return CameraResponse.model_validate(camera)
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error wh camera {camera_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch camera from database"
            )
        except Exception as e:
            logger.error(f"Unexpected error while fetching camera {camera_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred"
            )
    
    def get_cameras_by_direction(self, direction: str) -> List[CameraResponse]:
        """Retrieve all cameras with a specific direction.
        
        Args:
            direction: The direction to filter by
            
        Returns:
            List of CameraResponse objects
            
        Raises:
            HTTPException: If database query fails
        """
        try:
            logger.info(f"Fetching cameras with direction: {direction}")
            cameras = self.repository.get_by_direction(direction)
            logger.info(f"Successfully retrieved {len(cameras)} cameras with direction '{direction}'")
            return [CameraResponse.model_validate(cam) for cam in cameras]
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching cameras by direction {direction}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch cameras from database"
            )
        except Exception as e:
            logger.error(f"Unexpected error while fetching cameras by direction {direction}: {e}")
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred"
            )
    
    def create_camera(self, camera_data: CameraCreate, skip_online_check: bool = False) -> CameraResponse:
        """Create a new camera in the database.
        
        Args:
            camera_data: Validated camera data for creation
            skip_online_check: Skip online check before creating (default: False)
            
        Returns:
            CameraResponse object for the newly created camera
            
        Raises:
            HTTPException: If camera name already exists, camera is offline, or database error occurs
        """
        try:
            logger.info(f"Creating new camera: {camera_data.name}")
            
            # Check if camera name already exists
            if self.repository.exists_by_name(camera_data.name):
                logger.warning(f"Camera name already exists: {camera_data.name}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Camera with name '{camera_data.name}' already exists"
                )
            
            # Check if camera is online before creating (unless skipped)
            if not skip_online_check:
                logger.info(f"Checking if camera is online: {camera_data.url}")
                is_online = self.check_camera_online(camera_data.url)
                
                if not is_online:
                    logger.warning(f"Camera is offline, cannot add: {camera_data.name} - {camera_data.url}")
                    raise HTTPException(
                        status_code=400,
                        detail=f"Camera is offline or unreachable. Please check the URL and ensure the camera is online before adding."
                    )
                
                logger.info(f"Camera is online, proceeding with creation: {camera_data.name}")
                
                # Create new CameraCreate object with status set to online
                camera_dict = camera_data.model_dump()
                camera_dict['status'] = 'online'
                camera_data = CameraCreate(**camera_dict)
            
            camera = self.repository.create(camera_data)
            logger.info(f"Successfully created camera: {camera.name} (ID: {camera.id})")
            return CameraResponse.model_validate(camera)
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except IntegrityError as e:
            logger.error(f"Integrity constraint violated while creating camera: {e}")
            raise HTTPException(
                status_code=400,
                detail="Camera name already exists or constraint violation"
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error while creating camera: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to create camera in database"
            )
        except Exception as e:
            logger.error(f"Unexpected error while creating camera: {e}")
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred"
            )
    
    def update_camera(self, camera_id: str, camera_data: CameraUpdate) -> CameraResponse:
        """Update an existing camera in the database.
        
        Args:
            camera_id: The unique identifier of the camera to update
            camera_data: Validated camera data with fields to update
            
        Returns:
            CameraResponse object for the updated camera
            
        Raises:
            HTTPException: If camera not found, name conflict, or database error occurs
        """
        try:
            logger.info(f"Updating camera with ID: {camera_id}")
            
            # If updating name, check if new name already exists
            if camera_data.name and self.repository.exists_by_name(
                camera_data.name, exclude_id=camera_id
            ):
                logger.warning(f"Camera name already exists: {camera_data.name}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Camera with name '{camera_data.name}' already exists"
                )
            
            camera = self.repository.update(camera_id, camera_data)
            
            if not camera:
                logger.warning(f"Camera not found with ID: {camera_id}")
                raise HTTPException(
                    status_code=404,
                    detail=f"Camera with ID '{camera_id}' not found"
                )
            
            logger.info(f"Successfully updated camera: {camera.name} (ID: {camera.id})")
            return CameraResponse.model_validate(camera)
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except IntegrityError as e:
            logger.error(f"Integrity constraint violated while updating camera {camera_id}: {e}")
            raise HTTPException(
                status_code=400,
                detail="Camera name already exists or constraint violation"
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error while updating camera {camera_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to update camera in database"
            )
        except Exception as e:
            logger.error(f"Unexpected error while updating camera {camera_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred"
            )
    
    def delete_camera(self, camera_id: str) -> dict:
        """Delete a camera from the database.
        
        Args:
            camera_id: The unique identifier of the camera to delete
            
        Returns:
            Dictionary with success message
            
        Raises:
            HTTPException: If camera not found or database error occurs
        """
        try:
            logger.info(f"Deleting camera with ID: {camera_id}")
            success = self.repository.delete(camera_id)
            
            if not success:
                logger.warning(f"Camera not found with ID: {camera_id}")
                raise HTTPException(
                    status_code=404,
                    detail=f"Camera with ID '{camera_id}' not found"
                )
            
            logger.info(f"Successfully deleted camera with ID: {camera_id}")
            return {"message": "Camera deleted successfully"}
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error while deleting camera {camera_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to delete camera from database"
            )
        except Exception as e:
            logger.error(f"Unexpected error while deleting camera {camera_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred"
            )
    
    def update_camera_status(self, camera_id: str, status: str) -> CameraResponse:
        """Update the status of a camera.
        
        Args:
            camera_id: The unique identifier of the camera
            status: The new status ('online' or 'offline')
            
        Returns:
            CameraResponse object for the updated camera
            
        Raises:
            HTTPException: If camera not found or database error occurs
        """
        try:
            logger.info(f"Updating status for camera {camera_id} to: {status}")
            camera_data = CameraUpdate(status=status)
            result = self.update_camera(camera_id, camera_data)
            logger.info(f"Successfully updated status for camera {camera_id}")
            return result
        except Exception:
            # Let the update_camera method handle all exceptions
            raise
    
    def check_camera_online(self, camera_url: str, timeout: int = None) -> bool:
        """Check if a camera is online by attempting to connect to its stream.
        
        Args:
            camera_url: The URL of the camera stream (RTSP, HTTP, etc.)
            timeout: Connection timeout in seconds (default: from settings)
            
        Returns:
            bool: True if camera is online and accessible, False otherwise
        """
        try:
            if timeout is None:
                timeout = settings.CAMERA_CHECK_TIMEOUT_SECONDS
            
            logger.info(f"Checking camera online status: {camera_url}")
            
            # Create VideoCapture object with timeout
            cap = cv2.VideoCapture(camera_url)
            cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, timeout * 1000)
            
            # Try to open the stream
            if not cap.isOpened():
                logger.warning(f"Camera offline: Failed to open stream {camera_url}")
                cap.release()
                return False
            
            # Try to read a frame to verify the stream is working
            ret, frame = cap.read()
            cap.release()
            
            if ret and frame is not None:
                logger.info(f"Camera online: {camera_url}")
                return True
            else:
                logger.warning(f"Camera offline: Failed to read frame from {camera_url}")
                return False
                
        except Exception as e:
            logger.error(f"Error checking camera status for {camera_url}: {e}")
            return False
    
    def check_camera_status_by_id(self, camera_id: str) -> Dict[str, any]:
        """Check and update the online status of a specific camera.
        
        Args:
            camera_id: The unique identifier of the camera
            
        Returns:
            Dictionary with camera ID, current status, and check result
            
        Raises:
            HTTPException: If camera not found or database error occurs
        """
        try:
            logger.info(f"Checking status for camera ID: {camera_id}")
            
            # Get camera details
            camera = self.get_camera_by_id(camera_id)
            
            # Check if camera is online
            is_online = self.check_camera_online(camera.url)
            new_status = "online" if is_online else "offline"
            
            # Update status if changed
            if camera.status != new_status:
                logger.info(f"Camera {camera_id} status changed: {camera.status} -> {new_status}")
                self.update_camera_status(camera_id, new_status)
            
            return {
                "camera_id": camera_id,
                "camera_name": camera.name,
                "url": camera.url,
                "previous_status": camera.status,
                "current_status": new_status,
                "is_online": is_online,
                "status_changed": camera.status != new_status
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error checking camera status for {camera_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to check camera status: {str(e)}"
            )
    
    def check_all_cameras_status(self) -> Dict[str, any]:
        """Check and update the online status of all cameras.
        
        Returns:
            Dictionary with summary of all camera status checks
            
        Raises:
            HTTPException: If database error occurs
        """
        try:
            logger.info("Checking status for all cameras")
            
            cameras = self.get_all_cameras()
            results = []
            online_count = 0
            offline_count = 0
            changed_count = 0
            
            for camera in cameras:
                try:
                    # Check if camera is online
                    is_online = self.check_camera_online(camera.url)
                    new_status = "online" if is_online else "offline"
                    
                    # Update status if changed
                    status_changed = camera.status != new_status
                    if status_changed:
                        self.update_camera_status(camera.id, new_status)
                        changed_count += 1
                    
                    # Count online/offline
                    if is_online:
                        online_count += 1
                    else:
                        offline_count += 1
                    
                    results.append({
                        "camera_id": camera.id,
                        "camera_name": camera.name,
                        "url": camera.url,
                        "previous_status": camera.status,
                        "current_status": new_status,
                        "is_online": is_online,
                        "status_changed": status_changed
                    })
                    
                except Exception as e:
                    logger.error(f"Error checking camera {camera.id}: {e}")
                    results.append({
                        "camera_id": camera.id,
                        "camera_name": camera.name,
                        "url": camera.url,
                        "error": str(e),
                        "is_online": False
                    })
                    offline_count += 1
            
            logger.info(f"Status check complete: {online_count} online, {offline_count} offline, {changed_count} changed")
            
            return {
                "total_cameras": len(cameras),
                "online_count": online_count,
                "offline_count": offline_count,
                "status_changed_count": changed_count,
                "cameras": results
            }
            
        except Exception as e:
            logger.error(f"Error checking all cameras status: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to check cameras status: {str(e)}"
            )
