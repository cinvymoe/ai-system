"""Camera repository for database operations."""
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from src.models.camera import Camera
from src.schemas.camera import CameraCreate, CameraUpdate


class CameraRepository:
    """Repository class for camera data access operations.
    
    This class provides an abstraction layer over the database,
    handling all CRUD operations for Camera entities.
    """
    
    def __init__(self, db: Session):
        """Initialize the repository with a database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def get_all(self) -> List[Camera]:
        """Retrieve all cameras from the database.
        
        Returns:
            List of all Camera objects
        """
        return self.db.query(Camera).all()
    
    def get_by_id(self, camera_id: str) -> Optional[Camera]:
        """Retrieve a camera by its ID.
        
        Args:
            camera_id: The unique identifier of the camera
            
        Returns:
            Camera object if found, None otherwise
        """
        return self.db.query(Camera).filter(Camera.id == camera_id).first()
    
    def get_by_direction(self, direction: str) -> List[Camera]:
        """Retrieve all cameras with a specific direction.
        
        Args:
            direction: The direction to filter by (forward, backward, left, right, idle)
            
        Returns:
            List of Camera objects matching the direction
        """
        return self.db.query(Camera).filter(Camera.direction == direction).all()
    
    def create(self, camera_data: CameraCreate) -> Camera:
        """Create a new camera in the database.
        
        Args:
            camera_data: Validated camera data for creation
            
        Returns:
            The newly created Camera object with generated ID
        """
        camera = Camera(
            id=str(uuid.uuid4()),
            **camera_data.model_dump()
        )
        self.db.add(camera)
        self.db.commit()
        self.db.refresh(camera)
        return camera
    
    def update(self, camera_id: str, camera_data: CameraUpdate) -> Optional[Camera]:
        """Update an existing camera in the database.
        
        Args:
            camera_id: The unique identifier of the camera to update
            camera_data: Validated camera data with fields to update
            
        Returns:
            Updated Camera object if found, None otherwise
        """
        camera = self.get_by_id(camera_id)
        if not camera:
            return None
        
        # Only update fields that were explicitly set
        update_data = camera_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(camera, key, value)
        
        self.db.commit()
        self.db.refresh(camera)
        return camera
    
    def delete(self, camera_id: str) -> bool:
        """Delete a camera from the database.
        
        Args:
            camera_id: The unique identifier of the camera to delete
            
        Returns:
            True if camera was deleted, False if camera was not found
        """
        camera = self.get_by_id(camera_id)
        if not camera:
            return False
        
        self.db.delete(camera)
        self.db.commit()
        return True
    
    def exists_by_name(self, name: str, exclude_id: Optional[str] = None) -> bool:
        """Check if a camera with the given name exists.
        
        This is useful for enforcing unique name constraints and
        preventing duplicate camera names.
        
        Args:
            name: The camera name to check
            exclude_id: Optional camera ID to exclude from the check
                       (useful when updating a camera's name)
            
        Returns:
            True if a camera with the name exists, False otherwise
        """
        query = self.db.query(Camera).filter(Camera.name == name)
        if exclude_id:
            query = query.filter(Camera.id != exclude_id)
        return query.first() is not None
