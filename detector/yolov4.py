from detection import Detection, Detector
from geometry import Geometry
from models.yolov4.yolov4_model import Yolov4

import torch
import asyncio
import numpy as np

class yolo(Detector):
    def __init__(self, **kwargs):
        super(yolo, self).__init__(name='yolov4', **kwargs)
        self.model = Yolov4()
    
    def detect(self, img:np.ndarray):
        return asyncio.sleep(0)
        return []

yolo = YoloV4()