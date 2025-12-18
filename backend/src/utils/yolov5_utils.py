"""YOLOv5 utility functions for post-processing."""
import numpy as np
from typing import List, Tuple, Optional
import cv2


class YOLOv5PostProcessor:
    """YOLOv5 post-processing utilities."""
    
    def __init__(self, obj_thresh: float = 0.25, nms_thresh: float = 0.45, 
                 img_size: Tuple[int, int] = (640, 640)):
        """Initialize post-processor.
        
        Args:
            obj_thresh: Object confidence threshold
            nms_thresh: NMS IoU threshold
            img_size: Model input size (width, height)
        """
        self.obj_thresh = obj_thresh
        self.nms_thresh = nms_thresh
        self.img_size = img_size
    
    def filter_boxes(self, boxes: np.ndarray, box_confidences: np.ndarray, 
                    box_class_probs: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Filter boxes with object threshold.
        
        Args:
            boxes: Bounding boxes array
            box_confidences: Box confidence scores
            box_class_probs: Class probabilities
            
        Returns:
            Tuple of (filtered_boxes, classes, scores)
        """
        box_confidences = box_confidences.reshape(-1)
        class_max_score = np.max(box_class_probs, axis=-1)
        classes = np.argmax(box_class_probs, axis=-1)
        
        _class_pos = np.where(class_max_score * box_confidences >= self.obj_thresh)
        scores = (class_max_score * box_confidences)[_class_pos]
        boxes = boxes[_class_pos]
        classes = classes[_class_pos]
        
        return boxes, classes, scores
    
    def nms_boxes(self, boxes: np.ndarray, scores: np.ndarray) -> np.ndarray:
        """Suppress non-maximal boxes.
        
        Args:
            boxes: Bounding boxes array [N, 4] in format [x1, y1, x2, y2]
            scores: Confidence scores [N]
            
        Returns:
            Array of indices to keep
        """
        x = boxes[:, 0]
        y = boxes[:, 1]
        w = boxes[:, 2] - boxes[:, 0]
        h = boxes[:, 3] - boxes[:, 1]
        
        areas = w * h
        order = scores.argsort()[::-1]
        keep = []
        
        while order.size > 0:
            i = order[0]
            keep.append(i)
            
            xx1 = np.maximum(x[i], x[order[1:]])
            yy1 = np.maximum(y[i], y[order[1:]])
            xx2 = np.minimum(x[i] + w[i], x[order[1:]] + w[order[1:]])
            yy2 = np.minimum(y[i] + h[i], y[order[1:]] + h[order[1:]])
            
            w1 = np.maximum(0.0, xx2 - xx1 + 0.00001)
            h1 = np.maximum(0.0, yy2 - yy1 + 0.00001)
            
            inter = w1 * h1
            ovr = inter / (areas[i] + areas[order[1:]] - inter)
            
            inds = np.where(ovr <= self.nms_thresh)[0]
            order = order[inds + 1]
        
        return np.array(keep)
    
    def box_process(self, position: np.ndarray, anchors: List) -> np.ndarray:
        """Process box predictions from YOLOv5 output.
        
        Args:
            position: Position predictions [batch, 4, grid_h, grid_w]
            anchors: Anchor boxes for this scale
            
        Returns:
            Processed boxes in [x1, y1, x2, y2] format
        """
        grid_h, grid_w = position.shape[2:4]
        col, row = np.meshgrid(np.arange(0, grid_w), np.arange(0, grid_h))
        col = col.reshape(1, 1, grid_h, grid_w)
        row = row.reshape(1, 1, grid_h, grid_w)
        grid = np.concatenate((col, row), axis=1)
        stride = np.array([self.img_size[1]//grid_h, self.img_size[0]//grid_w]).reshape(1, 2, 1, 1)

        col = col.repeat(len(anchors), axis=0)
        row = row.repeat(len(anchors), axis=0)
        anchors = np.array(anchors)
        anchors = anchors.reshape(*anchors.shape, 1, 1)

        box_xy = position[:, :2, :, :] * 2 - 0.5
        box_wh = pow(position[:, 2:4, :, :] * 2, 2) * anchors

        box_xy += grid
        box_xy *= stride
        box = np.concatenate((box_xy, box_wh), axis=1)

        # Convert [c_x, c_y, w, h] to [x1, y1, x2, y2]
        xyxy = np.copy(box)
        xyxy[:, 0, :, :] = box[:, 0, :, :] - box[:, 2, :, :] / 2  # top left x
        xyxy[:, 1, :, :] = box[:, 1, :, :] - box[:, 3, :, :] / 2  # top left y
        xyxy[:, 2, :, :] = box[:, 0, :, :] + box[:, 2, :, :] / 2  # bottom right x
        xyxy[:, 3, :, :] = box[:, 1, :, :] + box[:, 3, :, :] / 2  # bottom right y

        return xyxy
    
    def post_process(self, input_data: List[np.ndarray], anchors: List) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[np.ndarray]]:
        """Post-process YOLOv5 model outputs.
        
        Args:
            input_data: List of output tensors from model
            anchors: Anchor boxes for all scales
            
        Returns:
            Tuple of (boxes, classes, scores) or (None, None, None) if no detections
        """
        if input_data is None:
            return None, None, None
            
        boxes, scores, classes_conf = [], [], []
        
        # Reshape: 1*255*h*w -> 3*85*h*w
        input_data = [_in.reshape([len(anchors[0]), -1] + list(_in.shape[-2:])) for _in in input_data]
        
        for i in range(len(input_data)):
            boxes.append(self.box_process(input_data[i][:, :4, :, :], anchors[i]))
            scores.append(input_data[i][:, 4:5, :, :])
            classes_conf.append(input_data[i][:, 5:, :, :])

        def sp_flatten(_in):
            ch = _in.shape[1]
            _in = _in.transpose(0, 2, 3, 1)
            return _in.reshape(-1, ch)

        boxes = [sp_flatten(_v) for _v in boxes]
        classes_conf = [sp_flatten(_v) for _v in classes_conf]
        scores = [sp_flatten(_v) for _v in scores]

        boxes = np.concatenate(boxes)
        classes_conf = np.concatenate(classes_conf)
        scores = np.concatenate(scores)

        # Filter according to threshold
        boxes, classes, scores = self.filter_boxes(boxes, scores, classes_conf)

        # NMS
        nboxes, nclasses, nscores = [], [], []
        for c in set(classes):
            inds = np.where(classes == c)
            b = boxes[inds]
            c_arr = classes[inds]
            s = scores[inds]
            keep = self.nms_boxes(b, s)

            if len(keep) != 0:
                nboxes.append(b[keep])
                nclasses.append(c_arr[keep])
                nscores.append(s[keep])

        if not nclasses and not nscores:
            return None, None, None

        boxes = np.concatenate(nboxes)
        classes = np.concatenate(nclasses)
        scores = np.concatenate(nscores)

        return boxes, classes, scores


class ImagePreprocessor:
    """Image preprocessing utilities for YOLOv5."""
    
    @staticmethod
    def letter_box(im: np.ndarray, new_shape: Tuple[int, int] = (640, 640), 
                   pad_color: Tuple[int, int, int] = (0, 0, 0)) -> np.ndarray:
        """Resize and pad image while maintaining aspect ratio.
        
        Args:
            im: Input image
            new_shape: Target size (height, width)
            pad_color: Padding color (B, G, R)
            
        Returns:
            Padded image
        """
        shape = im.shape[:2]  # current shape [height, width]
        
        # Scale ratio (new / old)
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        
        # Compute padding
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
        
        dw /= 2  # divide padding into 2 sides
        dh /= 2
        
        if shape[::-1] != new_unpad:  # resize
            im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
        
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=pad_color)
        
        return im
    
    @staticmethod
    def get_real_box(boxes: np.ndarray, original_shape: Tuple[int, int], 
                     new_shape: Tuple[int, int] = (640, 640)) -> np.ndarray:
        """Convert boxes from padded image coordinates to original image coordinates.
        
        Args:
            boxes: Bounding boxes [N, 4] in format [x1, y1, x2, y2]
            original_shape: Original image shape (height, width)
            new_shape: Model input shape (height, width)
            
        Returns:
            Boxes in original image coordinates
        """
        if boxes is None or len(boxes) == 0:
            return boxes
            
        # Calculate scale ratio (new / old)
        r = min(new_shape[0] / original_shape[0], new_shape[1] / original_shape[1])
        
        # Calculate padding
        new_unpad = int(round(original_shape[1] * r)), int(round(original_shape[0] * r))
        dw = (new_shape[1] - new_unpad[0]) / 2
        dh = (new_shape[0] - new_unpad[1]) / 2
        
        # Convert boxes back to original coordinates
        real_boxes = boxes.copy()
        real_boxes[:, 0] = (real_boxes[:, 0] - dw) / r  # x1
        real_boxes[:, 1] = (real_boxes[:, 1] - dh) / r  # y1  
        real_boxes[:, 2] = (real_boxes[:, 2] - dw) / r  # x2
        real_boxes[:, 3] = (real_boxes[:, 3] - dh) / r  # y2
        
        # Clip to original image boundaries
        real_boxes[:, [0, 2]] = np.clip(real_boxes[:, [0, 2]], 0, original_shape[1])
        real_boxes[:, [1, 3]] = np.clip(real_boxes[:, [1, 3]], 0, original_shape[0])
        
        return real_boxes
    
    @staticmethod
    def prepare_input(image: np.ndarray, platform: str = 'rknn') -> np.ndarray:
        """Prepare input tensor for model inference.
        
        Args:
            image: Preprocessed image (RGB format)
            platform: Model platform ('rknn', 'pytorch', 'onnx')
            
        Returns:
            Input tensor ready for inference
        """
        if platform in ['pytorch', 'onnx']:
            # Transpose to CHW format and normalize
            input_data = image.transpose((2, 0, 1))
            input_data = input_data.reshape(1, *input_data.shape).astype(np.float32)
            input_data = input_data / 255.0
        else:  # rknn
            # Keep HWC format, add batch dimension, no normalization
            input_data = np.expand_dims(image, axis=0)
        
        return input_data


class YOLOv5Visualizer:
    """Visualization utilities for YOLOv5 detections."""
    
    # COCO class names
    COCO_CLASSES = (
        "person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
        "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
        "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack",
        "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball",
        "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket",
        "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
        "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair",
        "sofa", "pottedplant", "bed", "diningtable", "toilet", "tvmonitor", "laptop", "mouse",
        "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator",
        "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
    )
    
    @classmethod
    def draw_detections(cls, image: np.ndarray, boxes: np.ndarray, 
                       scores: np.ndarray, classes: np.ndarray,
                       class_filter: Optional[int] = None,
                       color: Tuple[int, int, int] = (255, 0, 0),
                       thickness: int = 2) -> np.ndarray:
        """Draw detection results on image.
        
        Args:
            image: Input image (BGR format)
            boxes: Bounding boxes [N, 4] in format [x1, y1, x2, y2]
            scores: Confidence scores [N]
            classes: Class IDs [N]
            class_filter: Only draw this class ID (None = draw all)
            color: Box color (B, G, R)
            thickness: Line thickness
            
        Returns:
            Annotated image
        """
        img_annotated = image.copy()
        
        for box, score, cls in zip(boxes, scores, classes):
            # Filter by class if specified
            if class_filter is not None and cls != class_filter:
                continue
            
            top, left, right, bottom = [int(_b) for _b in box]
            class_name = YOLOv5Visualizer.COCO_CLASSES[int(cls)] if int(cls) < len(YOLOv5Visualizer.COCO_CLASSES) else f"class_{cls}"
            
            # Draw bounding box
            cv2.rectangle(img_annotated, (top, left), (right, bottom), color, thickness)
            
            # Draw label with background
            label = f'{class_name} {score:.2f}'
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            
            # Draw label background
            cv2.rectangle(img_annotated, 
                         (top, left - label_size[1] - 6),
                         (top + label_size[0], left),
                         color, -1)
            
            # Draw label text
            cv2.putText(img_annotated, label, (top, left - 6),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return img_annotated
    
    @classmethod
    def draw_person_only(cls, image: np.ndarray, boxes: np.ndarray,
                        scores: np.ndarray, classes: np.ndarray) -> np.ndarray:
        """Draw only person detections.
        
        Args:
            image: Input image (BGR format)
            boxes: Bounding boxes
            scores: Confidence scores
            classes: Class IDs
            
        Returns:
            Annotated image with person detections only
        """
        return cls.draw_detections(image, boxes, scores, classes, 
                                  class_filter=0, color=(255, 0, 0))
