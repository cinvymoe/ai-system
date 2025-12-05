"""Tests for CameraRepository."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.camera import Camera
from repositories.camera_repository import CameraRepository
from schemas.camera import CameraCreate, CameraUpdate


@pytest.fixture
def db_session():
    """Create a test database session."""
    # Use in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:")
    
    # Create tables using the Camera model's Base
    Camera.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()


@pytest.fixture
def repository(db_session):
    """Create a CameraRepository instance."""
    return CameraRepository(db_session)


@pytest.fixture
def sample_camera_data():
    """Sample camera data for testing."""
    return CameraCreate(
        name="Test Camera",
        url="rtsp://192.168.1.100:554/stream",
        enabled=True,
        resolution="1920x1080",
        fps=30,
        brightness=50,
        contrast=50,
        status="offline",
        direction="forward"
    )


def test_create_camera(repository, sample_camera_data):
    """Test creating a camera."""
    camera = repository.create(sample_camera_data)
    
    assert camera.id is not None
    assert camera.name == "Test Camera"
    assert camera.url == "rtsp://192.168.1.100:554/stream"
    assert camera.direction == "forward"
    assert camera.enabled is True


def test_get_all_cameras(repository, sample_camera_data):
    """Test retrieving all cameras."""
    # Create multiple cameras
    repository.create(sample_camera_data)
    
    camera_data_2 = CameraCreate(
        name="Test Camera 2",
        url="rtsp://192.168.1.101:554/stream",
        direction="backward"
    )
    repository.create(camera_data_2)
    
    cameras = repository.get_all()
    assert len(cameras) == 2


def test_get_by_id(repository, sample_camera_data):
    """Test retrieving a camera by ID."""
    created_camera = repository.create(sample_camera_data)
    
    retrieved_camera = repository.get_by_id(created_camera.id)
    assert retrieved_camera is not None
    assert retrieved_camera.id == created_camera.id
    assert retrieved_camera.name == "Test Camera"


def test_get_by_id_not_found(repository):
    """Test retrieving a non-existent camera."""
    camera = repository.get_by_id("non-existent-id")
    assert camera is None


def test_get_by_direction(repository, sample_camera_data):
    """Test retrieving cameras by direction."""
    # Create cameras with different directions
    repository.create(sample_camera_data)  # forward
    
    camera_data_2 = CameraCreate(
        name="Test Camera 2",
        url="rtsp://192.168.1.101:554/stream",
        direction="backward"
    )
    repository.create(camera_data_2)
    
    camera_data_3 = CameraCreate(
        name="Test Camera 3",
        url="rtsp://192.168.1.102:554/stream",
        direction="forward"
    )
    repository.create(camera_data_3)
    
    forward_cameras = repository.get_by_direction("forward")
    assert len(forward_cameras) == 2
    
    backward_cameras = repository.get_by_direction("backward")
    assert len(backward_cameras) == 1


def test_update_camera(repository, sample_camera_data):
    """Test updating a camera."""
    created_camera = repository.create(sample_camera_data)
    
    update_data = CameraUpdate(
        name="Updated Camera",
        brightness=75
    )
    
    updated_camera = repository.update(created_camera.id, update_data)
    assert updated_camera is not None
    assert updated_camera.name == "Updated Camera"
    assert updated_camera.brightness == 75
    # Other fields should remain unchanged
    assert updated_camera.url == "rtsp://192.168.1.100:554/stream"


def test_update_camera_not_found(repository):
    """Test updating a non-existent camera."""
    update_data = CameraUpdate(name="Updated Camera")
    updated_camera = repository.update("non-existent-id", update_data)
    assert updated_camera is None


def test_delete_camera(repository, sample_camera_data):
    """Test deleting a camera."""
    created_camera = repository.create(sample_camera_data)
    
    result = repository.delete(created_camera.id)
    assert result is True
    
    # Verify camera is deleted
    deleted_camera = repository.get_by_id(created_camera.id)
    assert deleted_camera is None


def test_delete_camera_not_found(repository):
    """Test deleting a non-existent camera."""
    result = repository.delete("non-existent-id")
    assert result is False


def test_exists_by_name(repository, sample_camera_data):
    """Test checking if a camera name exists."""
    repository.create(sample_camera_data)
    
    assert repository.exists_by_name("Test Camera") is True
    assert repository.exists_by_name("Non-existent Camera") is False


def test_exists_by_name_with_exclude(repository, sample_camera_data):
    """Test checking if a camera name exists with exclusion."""
    created_camera = repository.create(sample_camera_data)
    
    # Should return False when excluding the camera with that name
    assert repository.exists_by_name("Test Camera", exclude_id=created_camera.id) is False
    
    # Create another camera
    camera_data_2 = CameraCreate(
        name="Test Camera 2",
        url="rtsp://192.168.1.101:554/stream",
        direction="backward"
    )
    repository.create(camera_data_2)
    
    # Should return True when checking for "Test Camera 2" and excluding the first camera
    assert repository.exists_by_name("Test Camera 2", exclude_id=created_camera.id) is True
