import os
import geojson
import pathlib
import glob

from shapely.geometry.polygon import Polygon
from shapely.geometry import Point

fences_path = pathlib.Path('./fences/')

class Map():
	def __init__(self, file_name):
		path = pathlib.Path(file_name)
		if not path.parent == fences_path:
			path = fences_path.joinpath(path)
		mapfiles = glob.glob(str(fences_path.joinpath('*.geojson')))
		assert(str(path) in mapfiles)

		with open(path, 'r') as f:
			self.map = geojson.load(f)
			self.poly = Polygon([Point(lat, lng) for lng,lat in self.map.geometry.coordinates[0]])

	def inside(self, point):
		if type(point) is tuple:
			point = Point(point)
		if type(point) is list:
			point = Point(tuple(point))
		return self.poly.contains(point)
	
	def point_inside(self, x, y):
		return self.inside((x, y))