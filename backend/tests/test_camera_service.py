"""Tests for CameraService."""
import pytest
from unittest.mock import Mock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.camera import Camera
from repositories.camera_repository import CameraRepository
from services.camera_service import CameraService
from schemas.camera import CameraCreate, CameraUpdate


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
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
def service(repository):
    """Create a CameraService instance."""
    return CameraService(repository)


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


def test_get_all_cameras(service, sample_camera_data):
    """Test retrieving all cameras through service."""
    service.repository.create(sample_camera_data)
    
    cameras = service.get_all_cameras()
    assert len(cameras) == 1
    assert cameras[0].name == "Test Camera"


def test_get_camera_by_id(service, sample_camera_data):
    """Test retrieving a camera by ID through service."""
    created = service.repository.create(sample_camera_data)
    
    camera = service.get_camera_by_id(created.id)
    assert camera.id == created.id
    assert camera.name == "Test Camera"


def test_get_camera_by_id_not_found(service):
    """Test retrieving a non-existent camera raises 404."""
    with pytest.raises(HTTPException) as exc_info:
        service.get_camera_by_id("non-existent-id")
    
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()


def test_get_cameras_by_direction(service, sample_camera_data):
    """Test retrieving cameras by direction through service."""
    service.repository.create(sample_camera_data)
    
    cameras = service.get_cameras_by_direction("forward")
    assert len(cameras) == 1
    assert cameras[0].direction == "forward"


def test_create_camera(service, sample_camera_data):
    """Test creating a camera through service."""
    camera = service.create_camera(sample_camera_data)
    
    assert camera.id is not None
    assert camera.name == "Test Camera"
    assert camera.url == "rtsp://192.168.1.100:554/stream"


def test_create_camera_duplicate_name(service, sample_camera_data):
    """Test creating a camera with duplicate name raises 400."""
    service.create_camera(sample_camera_data)
    
    with pytest.raises(HTTPException) as exc_info:
        service.create_camera(sample_camera_data)
    
    assert exc_info.value.status_code == 400
    assert "already exists" in exc_info.value.detail.lower()


def test_update_camera(service, sample_camera_data):
    """Test updating a camera through service."""
    created = service.create_camera(sample_camera_data)
    
    update_data = CameraUpdate(name="Updated Camera", brightness=75)
    updated = service.update_camera(created.id, update_data)
    
    assert updated.name == "Updated Camera"
    assert updated.brightness == 75


def test_update_camera_not_found(service):
    """Test updating a non-existent camera raises 404."""
    update_data = CameraUpdate(name="Updated Camera")
    
    with pytest.raises(HTTPException) as exc_info:
        service.update_camera("non-existent-id", update_data)
    
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()


def test_update_camera_duplicate_name(service, sample_camera_data):
    """Test updating a camera with duplicate name raises 400."""
    camera1 = service.create_camera(sample_camera_data)
    
    camera_data_2 = CameraCreate(
        name="Test Camera 2",
        url="rtsp://192.168.1.101:554/stream",
        direction="backward"
    )
    camera2 = service.create_camera(camera_data_2)
    
    # Try to update camera2 with camera1's name
    update_data = CameraUpdate(name="Test Camera")
    
    with pytest.raises(HTTPException) as exc_info:
        service.update_camera(camera2.id, update_data)
    
    assert exc_info.value.status_code == 400
    assert "already exists" in exc_info.value.detail.lower()


def test_delete_camera(service, sample_camera_data):
    """Test deleting a camera through service."""
    created = service.create_camera(sample_camera_data)
    
    result = service.delete_camera(created.id)
    assert result["message"] == "Camera deleted successfully"
    
    # Verify camera is deleted
    with pytest.raises(HTTPException):
        service.get_camera_by_id(created.id)


def test_delete_camera_not_found(service):
    """Test deleting a non-existent camera raises 404."""
    with pytest.raises(HTTPException) as exc_info:
        service.delete_camera("non-existent-id")
    
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()


def test_update_camera_status(service, sample_camera_data):
    """Test updating camera status through service."""
    created = service.create_camera(sample_camera_data)
    
    updated = service.update_camera_status(created.id, "online")
    assert updated.status == "online"


def test_database_error_handling(service):
    """Test that database errors are properly handled and logged."""
    # Mock the repository to raise a SQLAlchemyError
    service.repository.get_all = Mock(side_effect=SQLAlchemyError("Database error"))
    
    with pytest.raises(HTTPException) as exc_info:
        service.get_all_cameras()
    
    assert exc_info.value.status_code == 500
    assert "database" in exc_info.value.detail.lower()


def test_integrity_error_handling(service, sample_camera_data):
    """Test that integrity errors are properly handled and logged."""
    # Mock the repository to raise an IntegrityError
    service.repository.create = Mock(side_effect=IntegrityError("", "", ""))
    
    with pytest.raises(HTTPException) as exc_info:
        service.create_camera(sample_camera_data)
    
    assert exc_info.value.status_code == 400
    assert "constraint" in exc_info.value.detail.lower() or "exists" in exc_info.value.detail.lower()


@patch('services.camera_service.logger')
def test_logging_on_create(mock_logger, service, sample_camera_data):
    """Test that operations are logged correctly."""
    service.create_camera(sample_camera_data)
    
    # Verify logging was called
    assert mock_logger.info.called
    # Check that the log contains the camera name
    log_calls = [str(call) for call in mock_logger.info.call_args_list]
    assert any("Test Camera" in str(call) for call in log_calls)


@patch('services.camera_service.logger')
def test_logging_on_error(mock_logger, service):
    """Test that errors are logged correctly."""
    with pytest.raises(HTTPException):
        service.get_camera_by_id("non-existent-id")
    
    # Verify warning was logged for not found
    assert mock_logger.warning.called
