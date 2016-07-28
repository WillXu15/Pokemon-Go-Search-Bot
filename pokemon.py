import json
import datetime
import os
import logging

import utils

import pokedex
from pgoapi import PGoApi
from pgoapi import utilities as pgoutil

from google.protobuf.internal import encoder
from geopy.geocoders import GoogleV3
from s2sphere import Cell, CellId, LatLng


pokedex = pokedex.import_pokedex()


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(module)10s] [%(levelname)5s] %(message)s')
# log level for http request class
logging.getLogger("requests").setLevel(logging.WARNING)
# log level for main pgoapi class
logging.getLogger("pgoapi").setLevel(logging.INFO)
# log level for internal pgoapi class
logging.getLogger("rpc_api").setLevel(logging.INFO)

def get_pos_by_name(loc_name):
	geolocator = GoogleV3()
	loc = geolocator.geocode(loc_name)

	if not loc:
		return None

	return (loc.latitude, loc.longitude, loc.altitude)

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

def load_config():
	filename = 'config.json'
	dirname = os.path.dirname(os.path.realpath(__file__))
	with open(os.path.join(dirname, filename)) as config_file:
		return json.load(config_file)

def find_pokemon(api, lat, lng):
	step_size = 0.0015
	step_limit = 16
	coords = utils.generate_spiral(lat, lng, step_size, step_limit)

	pokemons = []
	for coord in coords:
		lat = coord["lat"]
		lng = coord["lng"]

		api.set_position(lat, lng, 0)
		cell_ids = get_cell_ids(lat, lng)
		timestamps = [0,] * len(cell_ids)

		api.get_map_objects(latitude = pgoutil.f2i(lat), longitude = pgoutil.f2i(lng), since_timestamp_ms = timestamps, cell_id = cell_ids)
		response_dict = api.call()

		if 'GET_MAP_OBJECTS' in response_dict['responses']:
			if 'status' in response_dict['responses']['GET_MAP_OBJECTS']:
				if response_dict['responses']['GET_MAP_OBJECTS']['status'] == 1:
				 	for map_cell in response_dict['responses']['GET_MAP_OBJECTS']['map_cells']:
				 		if 'wild_pokemons' in map_cell:
							for pokemon in map_cell['wild_pokemons']:
								pokemons.append(pokemon)
	
	return {v['encounter_id']:v for v in pokemons}.values()

def init():
	config = load_config()
	print config
	pos = get_pos_by_name(config["loc"])

	api = PGoApi()
	api.set_position(*pos)
	try:
		if not api.login(config["auth"], config["username"], config["password"]):
			return None, None
	except Exception:
		print "error logging in"
		return None, None

	return api, pos

def find_pokemon_around_me():
	api, pos = init()
	if api == None or pos == None:
		return None

	return find_pokemon(api, pos[0], pos[1])

def main():
	print find_pokemon_around_me()

if __name__ == '__main__':
    main()
