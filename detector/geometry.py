import numpy as np
import itertools

'''
Represents a segment of an image
'''
class Geometry:
    def __init__(self,x=0,y=0,width=0,height=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.mask = None

    def area(self):
        return self.width * self.height

    # Compute IOU for two geometries
    def iou(self, other:'Geometry'):
        ((x1, x2), (y1, y2)) = ((self.x, other.x), (self.y, other.y))
        (upper_x, upper_y) = (max(x1, x2), max(y1, y2))
        (lower_x, lower_y) = (min(x1+self.width, x2+other.width), min(y1+self.height, y2+other.height))
        intersection = float(abs(max((lower_x - upper_x, 0)) * max((lower_y - upper_y, 0))))
        union = float(self.area() + other.area() - intersection)
        if intersection == 0 or union == 0:
            return 0
        return intersection/union