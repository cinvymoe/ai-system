"""Tests for camera API routes."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import models first to register them with Base
from models.camera import Camera  # Import Camera to register it with Base
from database import get_db, Base
from main import app

# Create test database - use in-memory database for tests
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=None  # Disable pooling for in-memory database
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override database dependency for testing."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create tables in test database BEFORE creating TestClient
Base.metadata.create_all(bind=test_engine)

# Override the dependency at module level
app.dependency_overrides[get_db] = override_get_db

# Create test client at module level (after dependency override and table creation)
client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_test_database():
    """Clean database before each test."""
    # Clear all data before each test
    yield
    # Clean up after test by dropping and recreating tables
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)


def pytest_sessionfinish(session, exitstatus):
    """Cleanup test database file after all tests complete."""
    import os
    test_db_path = Path(__file__).parent.parent / "test_vision_security.db"
    if test_db_path.exists():
        os.remove(test_db_path)


def test_get_all_cameras_empty():
    """Test getting all cameras when database is empty."""
    response = client.get("/api/cameras/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_camera():
    """Test creating a new camera."""
    camera_data = {
        "name": "Test Camera",
        "url": "rtsp://test.com/stream",
        "direction": "forward",
        "enabled": True,
        "resolution": "1920x1080",
        "fps": 30,
        "brightness": 50,
        "contrast": 50,
        "status": "offline"
    }
    
    response = client.post("/api/cameras/", json=camera_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == camera_data["name"]
    assert data["url"] == camera_data["url"]
    assert data["direction"] == camera_data["direction"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_get_all_cameras():
    """Test getting all cameras."""
    # Create two cameras
    camera1 = {
        "name": "Camera 1",
        "url": "rtsp://test1.com/stream",
        "direction": "forward"
    }
    camera2 = {
        "name": "Camera 2",
        "url": "rtsp://test2.com/stream",
        "direction": "backward"
    }
    
    client.post("/api/cameras/", json=camera1)
    client.post("/api/cameras/", json=camera2)
    
    response = client.get("/api/cameras/")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Camera 1"
    assert data[1]["name"] == "Camera 2"


def test_get_camera_by_id():
    """Test getting a camera by ID."""
    # Create a camera
    camera_data = {
        "name": "Test Camera",
        "url": "rtsp://test.com/stream",
        "direction": "forward"
    }
    
    create_response = client.post("/api/cameras/", json=camera_data)
    camera_id = create_response.json()["id"]
    
    # Get the camera
    response = client.get(f"/api/cameras/{camera_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == camera_id
    assert data["name"] == camera_data["name"]


def test_get_camera_by_id_not_found():
    """Test getting a non-existent camera."""
    response = client.get("/api/cameras/nonexistent-id")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_cameras_by_direction():
    """Test getting cameras by direction."""
    # Create cameras with different directions
    camera1 = {
        "name": "Forward Camera",
        "url": "rtsp://test1.com/stream",
        "direction": "forward"
    }
    camera2 = {
        "name": "Backward Camera",
        "url": "rtsp://test2.com/stream",
        "direction": "backward"
    }
    camera3 = {
        "name": "Another Forward Camera",
        "url": "rtsp://test3.com/stream",
        "direction": "forward"
    }
    
    client.post("/api/cameras/", json=camera1)
    client.post("/api/cameras/", json=camera2)
    client.post("/api/cameras/", json=camera3)
    
    # Get forward cameras
    response = client.get("/api/cameras/direction/forward")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert all(cam["direction"] == "forward" for cam in data)


def test_update_camera():
    """Test updating a camera."""
    # Create a camera
    camera_data = {
        "name": "Original Name",
        "url": "rtsp://test.com/stream",
        "direction": "forward"
    }
    
    create_response = client.post("/api/cameras/", json=camera_data)
    camera_id = create_response.json()["id"]
    
    # Update the camera
    update_data = {
        "name": "Updated Name",
        "brightness": 75
    }
    
    response = client.patch(f"/api/cameras/{camera_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["brightness"] == 75
    assert data["url"] == camera_data["url"]  # Unchanged field


def test_update_camera_not_found():
    """Test updating a non-existent camera."""
    update_data = {"name": "New Name"}
    response = client.patch("/api/cameras/nonexistent-id", json=update_data)
    assert response.status_code == 404


def test_delete_camera():
    """Test deleting a camera."""
    # Create a camera
    camera_data = {
        "name": "To Delete",
        "url": "rtsp://test.com/stream",
        "direction": "forward"
    }
    
    create_response = client.post("/api/cameras/", json=camera_data)
    camera_id = create_response.json()["id"]
    
    # Delete the camera
    response = client.delete(f"/api/cameras/{camera_id}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"].lower()
    
    # Verify it's deleted
    get_response = client.get(f"/api/cameras/{camera_id}")
    assert get_response.status_code == 404


def test_delete_camera_not_found():
    """Test deleting a non-existent camera."""
    response = client.delete("/api/cameras/nonexistent-id")
    assert response.status_code == 404


def test_update_camera_status():
    """Test updating camera status."""
    # Create a camera
    camera_data = {
        "name": "Status Test Camera",
        "url": "rtsp://test.com/stream",
        "direction": "forward",
        "status": "offline"
    }
    
    create_response = client.post("/api/cameras/", json=camera_data)
    camera_id = create_response.json()["id"]
    
    # Update status
    response = client.patch(f"/api/cameras/{camera_id}/status?status=online")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "online"


def test_create_camera_duplicate_name():
    """Test creating a camera with duplicate name."""
    camera_data = {
        "name": "Duplicate Name",
        "url": "rtsp://test.com/stream",
        "direction": "forward"
    }
    
    # Create first camera
    response1 = client.post("/api/cameras/", json=camera_data)
    assert response1.status_code == 201
    
    # Try to create second camera with same name
    response2 = client.post("/api/cameras/", json=camera_data)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"].lower()


def test_create_camera_invalid_url():
    """Test creating a camera with invalid URL format."""
    camera_data = {
        "name": "Invalid URL Camera",
        "url": "http://test.com/stream",  # Should be rtsp://
        "direction": "forward"
    }
    
    response = client.post("/api/cameras/", json=camera_data)
    assert response.status_code == 422  # Validation error


def test_create_camera_invalid_resolution():
    """Test creating a camera with invalid resolution."""
    camera_data = {
        "name": "Invalid Resolution Camera",
        "url": "rtsp://test.com/stream",
        "direction": "forward",
        "resolution": "invalid"
    }
    
    response = client.post("/api/cameras/", json=camera_data)
    assert response.status_code == 422  # Validation error
