"""Camera API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

try:
    from database import get_db
    from repositories.camera_repository import CameraRepository
    from services.camera_service import CameraService
    from schemas.camera import CameraCreate, CameraUpdate, CameraResponse
except ImportError:
    from src.database import get_db
    from src.repositories.camera_repository import CameraRepository
    from src.services.camera_service import CameraService
    from src.schemas.camera import CameraCreate, CameraUpdate, CameraResponse

router = APIRouter(prefix="/api/cameras", tags=["cameras"])


def get_camera_service(db: Session = Depends(get_db)) -> CameraService:
    """Dependency injection for CameraService.
    
    Creates a CameraService instance with the required repository.
    This function is used as a FastAPI dependency to provide
    the service to route handlers.
    
    Args:
        db: Database session from get_db dependency
        
    Returns:
        CameraService: Configured camera service instance
    """
    repository = CameraRepository(db)
    return CameraService(repository)


@router.get("/", response_model=List[CameraResponse])
async def get_all_cameras(
    service: CameraService = Depends(get_camera_service)
):
    """Get all cameras.
    
    Retrieves all cameras from the database.
    
    Args:
        service: Camera service instance (injected)
        
    Returns:
        List[CameraResponse]: List of all cameras
        
    Raises:
        HTTPException: If database query fails
    """
    return service.get_all_cameras()


@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(
    camera_id: str,
    service: CameraService = Depends(get_camera_service)
):
    """Get a single camera by ID.
    
    Retrieves a specific camera from the database by its unique identifier.
    
    Args:
        camera_id: The unique identifier of the camera
        service: Camera service instance (injected)
        
    Returns:
        CameraResponse: The requested camera
        
    Raises:
        HTTPException: If camera not found (404) or database error (500)
    """
    return service.get_camera_by_id(camera_id)


@router.get("/direction/{direction}", response_model=List[CameraResponse])
async def get_cameras_by_direction(
    direction: str,
    service: CameraService = Depends(get_camera_service)
):
    """Get cameras by direction.
    
    Retrieves all cameras with a specific direction.
    
    Args:
        direction: The direction to filter by (forward, backward, left, right, idle)
        service: Camera service instance (injected)
        
    Returns:
        List[CameraResponse]: List of cameras with the specified direction
        
    Raises:
        HTTPException: If database query fails
    """
    return service.get_cameras_by_direction(direction)


@router.post("/", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
async def create_camera(
    camera: CameraCreate,
    skip_online_check: bool = False,
    service: CameraService = Depends(get_camera_service)
):
    """Create a new camera.
    
    Creates a new camera in the database with the provided data.
    By default, checks if the camera is online before adding.
    
    Args:
        camera: Camera data for creation
        skip_online_check: Skip online check (for batch imports, default: False)
        service: Camera service instance (injected)
        
    Returns:
        CameraResponse: The newly created camera
        
    Raises:
        HTTPException: If camera is offline (400), name already exists (400), or database error (500)
    """
    return service.create_camera(camera, skip_online_check=skip_online_check)


@router.patch("/{camera_id}", response_model=CameraResponse)
async def update_camera(
    camera_id: str,
    camera: CameraUpdate,
    service: CameraService = Depends(get_camera_service)
):
    """Update an existing camera.
    
    Updates a camera's information in the database. Only provided fields
    will be updated; omitted fields will remain unchanged.
    
    Args:
        camera_id: The unique identifier of the camera to update
        camera: Camera data with fields to update
        service: Camera service instance (injected)
        
    Returns:
        CameraResponse: The updated camera
        
    Raises:
        HTTPException: If camera not found (404), name conflict (400), or database error (500)
    """
    return service.update_camera(camera_id, camera)


@router.delete("/{camera_id}", status_code=status.HTTP_200_OK)
async def delete_camera(
    camera_id: str,
    service: CameraService = Depends(get_camera_service)
):
    """Delete a camera.
    
    Removes a camera from the database.
    
    Args:
        camera_id: The unique identifier of the camera to delete
        service: Camera service instance (injected)
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If camera not found (404) or database error (500)
    """
    return service.delete_camera(camera_id)


@router.patch("/{camera_id}/status", response_model=CameraResponse)
async def update_camera_status(
    camera_id: str,
    status: str,
    service: CameraService = Depends(get_camera_service)
):
    """Update camera status.
    
    Updates only the status field of a camera (online/offline).
    
    Args:
        camera_id: The unique identifier of the camera
        status: The new status ('online' or 'offline')
        service: Camera service instance (injected)
        
    Returns:
        CameraResponse: The updated camera
        
    Raises:
        HTTPException: If camera not found (404) or database error (500)
    """
    return service.update_camera_status(camera_id, status)


@router.post("/{camera_id}/check-status")
async def check_camera_status(
    camera_id: str,
    service: CameraService = Depends(get_camera_service)
):
    """Check if a specific camera is online.
    
    Attempts to connect to the camera stream and updates its status.
    
    Args:
        camera_id: The unique identifier of the camera
        service: Camera service instance (injected)
        
    Returns:
        dict: Camera status check result with details
        
    Raises:
        HTTPException: If camera not found (404) or check fails (500)
    """
    return service.check_camera_status_by_id(camera_id)


@router.post("/check-all-status")
async def check_all_cameras_status(
    service: CameraService = Depends(get_camera_service)
):
    """Check if all cameras are online.
    
    Attempts to connect to all camera streams and updates their status.
    
    Args:
        service: Camera service instance (injected)
        
    Returns:
        dict: Summary of all camera status checks
        
    Raises:
        HTTPException: If check fails (500)
    """
    return service.check_all_cameras_status()


@router.get("/monitor/status")
async def get_monitor_status():
    """Get camera monitor status.
    
    Returns information about the automatic camera monitoring service.
    
    Returns:
        dict: Monitor status including running state, check interval, and statistics
    """
    try:
        from scheduler.camera_monitor import get_camera_monitor
    except ImportError:
        from src.scheduler.camera_monitor import get_camera_monitor
    
    monitor = get_camera_monitor()
    return monitor.get_status()
