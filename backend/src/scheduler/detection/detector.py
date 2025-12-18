"""PersonDetector class - YOLOv5-based person detection."""

import logging
import os
import cv2
import numpy as np
from typing import Optional, List, Dict, Tuple

try:
    from utils.yolov5_utils import YOLOv5PostProcessor, ImagePreprocessor, YOLOv5Visualizer
except ImportError:
    from src.utils.yolov5_utils import YOLOv5PostProcessor, ImagePreprocessor, YOLOv5Visualizer

from .constants import OBJ_THRESH, NMS_THRESH, IMG_SIZE, PERSON_CLASS_ID, DEFAULT_ANCHORS

logger = logging.getLogger(__name__)


class PersonDetector:
    """YOLOv5-based person detection for camera streams - Refactored with utility classes."""
    
    def __init__(self, model_path: str, anchors: Optional[List] = None, target: str = 'rk3576', 
                 device_id: Optional[str] = None, obj_thresh: float = OBJ_THRESH, 
                 nms_thresh: float = NMS_THRESH):
        """Initialize person detector.
        
        Args:
            model_path: Path to YOLOv5 model (.rknn, .pt, or .onnx)
            anchors: Custom anchors (optional, uses defaults if not provided)
            target: Target RKNPU platform (default: rk3576)
            device_id: Device ID for RKNN (optional)
            obj_thresh: Object confidence threshold (default: 0.25)
            nms_thresh: NMS IoU threshold (default: 0.45)
        """
        self.model_path = model_path
        self.anchors = anchors or DEFAULT_ANCHORS
        self.target = target
        self.device_id = device_id
        self.model = None
        self.platform = None
        
        # Initialize utility classes
        self.post_processor = YOLOv5PostProcessor(obj_thresh, nms_thresh, IMG_SIZE)
        self.preprocessor = ImagePreprocessor()
        self.visualizer = YOLOv5Visualizer()
        
        self._setup_model()
    
    def _setup_model(self):
        """Setup the detection model based on file extension."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        
        try:
            if self.model_path.endswith('.pt') or self.model_path.endswith('.torchscript'):
                self.platform = 'pytorch'
                logger.info(f"Loading PyTorch model from {self.model_path}")
                try:
                    from utils.pytorch_executor import Torch_model_container
                    self.model = Torch_model_container(self.model_path)
                except ImportError:
                    logger.warning("PyTorch executor not available, model loading deferred")
                    
            elif self.model_path.endswith('.rknn'):
                self.platform = 'rknn'
                logger.info(f"Loading RKNN model from {self.model_path}")
                try:
                    from utils.rknn_executor import RKNN_model_container
                    self.model = RKNN_model_container(self.model_path, self.target, self.device_id)
                except ImportError:
                    logger.warning("RKNN executor not available, model loading deferred")
                
            elif self.model_path.endswith('.onnx'):
                self.platform = 'onnx'
                logger.info(f"Loading ONNX model from {self.model_path}")
                try:
                    from utils.onnx_executor import ONNX_model_container
                    self.model = ONNX_model_container(self.model_path)
                except ImportError:
                    logger.warning("ONNX executor not available, model loading deferred")
            else:
                raise ValueError(f"Unsupported model format: {self.model_path}")
                
            logger.info(f"Model loaded successfully - Platform: {self.platform}")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def detect_persons(self, frame: np.ndarray) -> List[Dict]:
        """Detect persons in a frame.
        
        Args:
            frame: Input image frame (BGR format)
            
        Returns:
            List of detection results with bounding boxes and scores
        """
        if frame is None or frame.size == 0:
            return []
        
        if self.model is None:
            logger.warning("Model not loaded, cannot perform detection")
            return []
        
        try:
            original_shape = frame.shape[:2]
            
            img = self.preprocessor.letter_box(
                frame.copy(), 
                new_shape=(IMG_SIZE[1], IMG_SIZE[0]), 
                pad_color=(0, 0, 0)
            )
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            input_data = self.preprocessor.prepare_input(img, self.platform)
            outputs = self.model.run([input_data])
            
            boxes, classes, scores = self.post_processor.post_process(outputs, self.anchors)
            
            if boxes is None or classes is None or scores is None:
                return []
            
            boxes = self.preprocessor.get_real_box(boxes, original_shape, (IMG_SIZE[1], IMG_SIZE[0]))
            
            person_detections = [
                {
                    'bbox': box.tolist(),
                    'score': float(score),
                    'class': 'person',
                    'class_id': int(cls)
                }
                for box, cls, score in zip(boxes, classes, scores)
                if cls == PERSON_CLASS_ID
            ]
            
            return person_detections
            
        except Exception as e:
            logger.error(f"Error during person detection: {e}", exc_info=True)
            return []
    
    def detect_and_draw(self, frame: np.ndarray, draw_all: bool = False) -> Tuple[np.ndarray, List[Dict]]:
        """Detect persons and draw bounding boxes on frame.
        
        Args:
            frame: Input image frame (BGR format)
            draw_all: If True, draw all detected objects; if False, only draw persons
            
        Returns:
            Tuple of (annotated frame, list of detections)
        """
        if frame is None or frame.size == 0:
            return frame, []
        
        if self.model is None:
            logger.warning("Model not loaded, cannot perform detection")
            return frame, []
        
        try:
            original_shape = frame.shape[:2]
            
            img = self.preprocessor.letter_box(
                frame.copy(),
                new_shape=(IMG_SIZE[1], IMG_SIZE[0]),
                pad_color=(0, 0, 0)
            )
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            input_data = self.preprocessor.prepare_input(img_rgb, self.platform)
            outputs = self.model.run([input_data])
            
            boxes, classes, scores = self.post_processor.post_process(outputs, self.anchors)
            
            if boxes is None or classes is None or scores is None:
                return frame, []
            
            boxes = self.preprocessor.get_real_box(boxes, original_shape, (IMG_SIZE[1], IMG_SIZE[0]))
            
            if draw_all:
                img_annotated = self.visualizer.draw_detections(frame, boxes, scores, classes)
            else:
                img_annotated = self.visualizer.draw_person_only(frame, boxes, scores, classes)
            
            detections = []
            for box, cls, score in zip(boxes, classes, scores):
                if not draw_all and cls != PERSON_CLASS_ID:
                    continue
                    
                class_name = self.visualizer.COCO_CLASSES[int(cls)] if int(cls) < len(self.visualizer.COCO_CLASSES) else f"class_{cls}"
                detections.append({
                    'bbox': box.tolist(),
                    'score': float(score),
                    'class': class_name,
                    'class_id': int(cls)
                })
            
            return img_annotated, detections
            
        except Exception as e:
            logger.error(f"Error during detection and drawing: {e}", exc_info=True)
            return frame, []
    
    def release(self):
        """Release model resources."""
        if self.model is not None:
            try:
                self.model.release()
                logger.info("Model resources released")
            except Exception as e:
                logger.error(f"Error releasing model: {e}")
