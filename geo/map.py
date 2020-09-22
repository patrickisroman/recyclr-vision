import geopandas
import pathlib
import glob
import random
from shapely.geometry import Point

fences_path = pathlib.Path('./fences/')

'''
We don't use projections for geofence calculations because with relatively small
map sizes, error without projection is significantly below the margin of error
for GPS localization. However, geopandas makes it relatively easy if needed.
'''

class Map():
	def __init__(self, file_name):
		self.gdf = self.__load_mapfile(file_name)
		self.detections = []

	def __load_mapfile(self, file_name):
		path = pathlib.Path(file_name)
		if not path.parent == fences_path:
			path = fences_path.joinpath(path)

		mapfiles = glob.glob(str(fences_path.joinpath('*.geojson')))
		assert str(path) in mapfiles, "Map file %s does not exist within path: %s" % (path, fences_path)
		return geopandas.read_file(str(path))

	def inside(self, x, y=None):
		if type(x) in (int, float):
			return self.gdf.contains(Point(x, y)).bool()
		elif type(x) is Point:
			return self.gdf.contains(x)

	def generate_points(self, n=1, point=None, radius_meters=0, distribution:str='uniform'):
		assert self.inside(point)
		points = []

		while len(points) < n:
			new_point = Point(
				point[0] + radius_meters * random.uniform(-1, 1),
				point[1] + radius_meters * random.uniform(-1, 1)) 
			if self.inside(new_point):
				points.append(new_point)
			
		return points
	
	def detection_exists(self, point=None, radius_meters:int=0, val:int=0):
		for p in self.detections:
			if p.distance(point) <= radius_meters:
				if p.val() == val:
					return True
		return False