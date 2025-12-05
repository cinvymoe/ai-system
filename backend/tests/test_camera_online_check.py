"""Tests for camera online check functionality."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException

from src.services.camera_service import CameraService
from src.repositories.camera_repository import CameraRepository
from src.schemas.camera import CameraResponse


@pytest.fixture
def mock_repository():
    """Create a mock camera repository."""
    return Mock(spec=CameraRepository)


@pytest.fixture
def camera_service(mock_repository):
    """Create a camera service with mock repository."""
    return CameraService(mock_repository)


@pytest.fixture
def sample_camera():
    """Create a sample camera response."""
    return CameraResponse(
        id="cam-001",
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


class TestCameraOnlineCheck:
    """Test cases for camera online check functionality."""
    
    @patch('src.services.camera_service.cv2.VideoCapture')
    def test_check_camera_online_success(self, mock_video_capture, camera_service):
        """Test successful camera online check."""
        # Setup mock
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, MagicMock())  # ret=True, frame=mock
        mock_video_capture.return_value = mock_cap
        
        # Test
        result = camera_service.check_camera_online("rtsp://192.168.1.100:554/stream")
        
        # Verify
        assert result is True
        mock_video_capture.assert_called_once_with("rtsp://192.168.1.100:554/stream")
        mock_cap.set.assert_called_once()
        mock_cap.isOpened.assert_called_once()
        mock_cap.read.assert_called_once()
        mock_cap.release.assert_called_once()
    
    @patch('src.services.camera_service.cv2.VideoCapture')
    def test_check_camera_online_failed_to_open(self, mock_video_capture, camera_service):
        """Test camera online check when stream fails to open."""
        # Setup mock
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_video_capture.return_value = mock_cap
        
        # Test
        result = camera_service.check_camera_online("rtsp://192.168.1.100:554/stream")
        
        # Verify
        assert result is False
        mock_cap.release.assert_called_once()
    
    @patch('src.services.camera_service.cv2.VideoCapture')
    def test_check_camera_online_failed_to_read_frame(self, mock_video_capture, camera_service):
        """Test camera online check when frame read fails."""
        # Setup mock
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (False, None)  # Failed to read
        mock_video_capture.return_value = mock_cap
        
        # Test
        result = camera_service.check_camera_online("rtsp://192.168.1.100:554/stream")
        
        # Verify
        assert result is False
        mock_cap.release.assert_called_once()
    
    @patch('src.services.camera_service.cv2.VideoCapture')
    def test_check_camera_online_exception(self, mock_video_capture, camera_service):
        """Test camera online check when exception occurs."""
        # Setup mock to raise exception
        mock_video_capture.side_effect = Exception("Connection error")
        
        # Test
        result = camera_service.check_camera_online("rtsp://192.168.1.100:554/stream")
        
        # Verify
        assert result is False
    
    @patch.object(CameraService, 'check_camera_online')
    @patch.object(CameraService, 'get_camera_by_id')
    @patch.object(CameraService, 'update_camera_status')
    def test_check_camera_status_by_id_online(
        self, mock_update_status, mock_get_camera, mock_check_online, 
        camera_service, sample_camera
    ):
        """Test checking camera status by ID when camera is online."""
        # Setup mocks
        mock_get_camera.return_value = sample_camera
        mock_check_online.return_value = True
        
        # Test
        result = camera_service.check_camera_status_by_id("cam-001")
        
        # Verify
        assert result["camera_id"] == "cam-001"
        assert result["is_online"] is True
        assert result["current_status"] == "online"
        assert result["previous_status"] == "offline"
        assert result["status_changed"] is True
        mock_update_status.assert_called_once_with("cam-001", "online")
    
    @patch.object(CameraService, 'check_camera_online')
    @patch.object(CameraService, 'get_camera_by_id')
    @patch.object(CameraService, 'update_camera_status')
    def test_check_camera_status_by_id_offline(
        self, mock_update_status, mock_get_camera, mock_check_online,
        camera_service, sample_camera
    ):
        """Test checking camera status by ID when camera is offline."""
        # Setup mocks
        mock_get_camera.return_value = sample_camera
        mock_check_online.return_value = False
        
        # Test
        result = camera_service.check_camera_status_by_id("cam-001")
        
        # Verify
        assert result["camera_id"] == "cam-001"
        assert result["is_online"] is False
        assert result["current_status"] == "offline"
        assert result["status_changed"] is False
        mock_update_status.assert_not_called()  # Status didn't change
    
    @patch.object(CameraService, 'check_camera_online')
    @patch.object(CameraService, 'get_all_cameras')
    @patch.object(CameraService, 'update_camera_status')
    def test_check_all_cameras_status(
        self, mock_update_status, mock_get_all, mock_check_online,
        camera_service, sample_camera
    ):
        """Test checking status for all cameras."""
        # Setup mocks
        camera1 = sample_camera
        camera2 = CameraResponse(
            id="cam-002",
            name="Test Camera 2",
            url="rtsp://192.168.1.101:554/stream",
            enabled=True,
            resolution="1920x1080",
            fps=30,
            brightness=50,
            contrast=50,
            status="online",
            direction="backward"
        )
        mock_get_all.return_value = [camera1, camera2]
        mock_check_online.side_effect = [True, False]  # cam1 online, cam2 offline
        
        # Test
        result = camera_service.check_all_cameras_status()
        
        # Verify
        assert result["total_cameras"] == 2
        assert result["online_count"] == 1
        assert result["offline_count"] == 1
        assert result["status_changed_count"] == 2  # Both changed
        assert len(result["cameras"]) == 2
        
        # Verify update_status was called for both cameras
        assert mock_update_status.call_count == 2
