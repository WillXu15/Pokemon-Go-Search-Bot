import random

from geopy.geocoders import GoogleV3
from s2sphere import Cell, CellId, LatLng

def get_cell_ids(lat, lng, radius=10):
    origin = CellId.from_lat_lng(LatLng.from_degrees(lat, lng)).parent(15)
    walk = [origin.id()]
    right = origin.next()
    left = origin.prev()

    for i in range(radius):
        walk.append(right.id())
        walk.append(left.id())
        right = right.next()
        left = left.prev()

    return sorted(walk)

def get_pos_by_name(loc_name):
    geolocator = GoogleV3()
    loc = geolocator.geocode(loc_name)

    if not loc:
        return None

    return (loc.latitude, loc.longitude, loc.altitude)

def generate_spiral(starting_lat, starting_lng, step_size, step_limit):
    coords = [{'lat': starting_lat, 'lng': starting_lng}]
    steps,x,y,d,m = 1, 0, 0, 1, 1
    rlow = 0.0
    rhigh = 0.0005

    while steps < step_limit:
        while 2 * x * d < m and steps < step_limit:
            x = x + d
            steps += 1
            lat = x * step_size + starting_lat + random.uniform(rlow, rhigh)
            lng = y * step_size + starting_lng + random.uniform(rlow, rhigh)
            coords.append({'lat': lat, 'lng': lng})
        while 2 * y * d < m and steps < step_limit:
            y = y + d
            steps += 1
            lat = x * step_size + starting_lat + random.uniform(rlow, rhigh)
            lng = y * step_size + starting_lng + random.uniform(rlow, rhigh)
            coords.append({'lat': lat, 'lng': lng})

        d = -1 * d
        m = m + 1
    return coords