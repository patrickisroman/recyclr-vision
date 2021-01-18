from typing import List
from pathlib import Path
from geometry import Geometry

import numpy as np

class Detection:
    def __init__(self):
        self.element:Enum = None
        self.material:Enum = None
        self.geometry:Geometry = None
        self.quality = 0.0
        self.weight = 0.0

class Detector(object):
    def __init__(self, name):
        self.__name = name
    
    def detect(img:np.ndarray) -> List[Detection]:
        pass

    def name(self):
        return self.__name
