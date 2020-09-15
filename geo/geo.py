import map

# static IP -> latlon, used for testing
import geocoder

class GeoManager():
    def __init__(self, file_name='alki.geojson'):
        self.map = map.Map(file_name)
        self.latlng = geocoder.ip('me').latlng