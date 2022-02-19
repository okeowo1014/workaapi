import geopy
import requests

Location = geopy.Nominatim(user_agent='Location App')


class Place:
    def __init__(self, placename):
        self.placename = placename
        self.Location = Location.geocode(self.placename)

    @property
    def lat(self):
        latitude = self.Location.raw['lat']
        return latitude

    @property
    def long(self):
        longtitude = self.Location.raw['lon']
        return longtitude

    @property
    def place_id(self):
        place_id = self.Location.raw['place_id']
        return place_id

    @property
    def address(self):
        return self.Location.address

    def get_nearby_city(self):
        result = requests.get(
            'http://api.geonames.org/findNearbyPlaceNameJSON?lat={}&lng={}&username=okeowo1014&localCountry'
            '=true&radius=300&cities=cities5000&style=short&maxRows=100'.format(
                self.lat,
                self.long))
        return result.json()

# Place('abeokuta').get_nearby_city()
# get_nearby_place = Location.reverse(
#     'localCountry=true&radius=300&cities=cities5000&style=short&maxRows=100&lat=7.1475&long=3.361')
# print(get_nearby_place)
