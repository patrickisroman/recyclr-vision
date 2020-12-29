from pathlib import Path
from .geometry import Geometry

class Detection:
    def __init__(self):
        self.element:Enum = None
        self.material:Enum = None
        self.geometry:Geometry = None
        self.quality = 0.0
        self.weight = 0.0