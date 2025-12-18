"""Constants for person detection module."""

# Detection parameters
OBJ_THRESH = 0.25
NMS_THRESH = 0.45
IMG_SIZE = (640, 640)  # (width, height)
PERSON_CLASS_ID = 0  # Person class in COCO dataset

# YOLOv5 default anchors
DEFAULT_ANCHORS = [
    [[10, 13], [16, 30], [33, 23]], 
    [[30, 61], [62, 45], [59, 119]], 
    [[116, 90], [156, 198], [373, 326]]
]
