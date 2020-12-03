import geopandas
import geojsonio
import pathlib
import glob
import random
import os

from typing import List
from shapely.geometry import Point

geo_dir = pathlib.Path(__file__).parent
fences_path = pathlib.Path.joinpath(geo_dir, 'fences')

'''
We don't use projections for geofence/map calculations because with relatively small
map sizes, error without projection is significantly below the margin of error
for GPS localization (um). However, geopandas makes it relatively easy if needed.
'''

class Map():
	def __init__(self, file_name):
		self.gdf = self.__load_mapfile(file_name)

	def __load_mapfile(self, file_name) -> 'GeoDataFrame':
		path = pathlib.Path(file_name)
		if not path.parent == fences_path:
			path = fences_path.joinpath(path)

		mapfiles = glob.glob(str(fences_path.joinpath('*.geojson')))
		assert str(path) in mapfiles, "Map file %s does not exist within path: %s" % (path, fences_path)
		return geopandas.read_file(str(path))

	def inside(self, lat, lon=None) -> bool:
		if type(lat) in (int, float):
			return self.gdf.contains(Point(lon, lat)).bool()
		elif type(lat) is Point:
			return self.gdf.contains(lat).bool()
		return False
	
	def display(self):
		geojsonio.display(self.gdf.to_json())

	def generate_points(self, n=1, point=None, radius_meters=0, distribution='uniform') -> List[Point]:
		assert self.inside(point)
		points = []

		sampling = {
			'uniform' : {
				'fn' : random.uniform,
				'args' : dict(a=-1, b=1)
			},
			'gaussian' : {
				'fn' : random.gauss,
				'args' : dict(mu=0, sigma=1)
			},
			'betavariate' : {
				'fn' : random.betavariate,
				'args' : dict(alpha=0, beta=1)
			}
		}
		
		s = sampling[distribution]

		while len(points) < n:
			lat = point[0] + radius_meters * s['fn'](**s['args'])
			lng = point[1] + radius_meters * s['fn'](**s['args'])

			if self.inside(lat, lng):
				points.append(Point(lat, lng))
			
		return points