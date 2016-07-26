import json
import datetime

import utils

import pokedex
from pgoapi import PGoApi
from pgoapi import utilities as pgoutil

from google.protobuf.internal import encoder
from geopy.geocoders import GoogleV3
from s2sphere import Cell, CellId, LatLng


pokedex = pokedex.import_pokedex()

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
	with open("config.json") as config_file:
		return json.load(config_file)

def find_pokemon(api, lat, lng):
	step_size = 0.0015
	step_limit = 16
	coords = utils.generate_spiral(lat, lng, step_size, step_limit)


	for coord in coords:
		lat = coord["lat"]
		lng = coord["lng"]

		api.set_position(lat, lng, 0)
		cell_ids = get_cell_ids(lat, lng)
		timestamps = [0,] * len(cell_ids)

		api.get_map_objects(latitude = pgoutil.f2i(lat), longitude = pgoutil.f2i(lng), since_timestamp_ms = timestamps, cell_id = cell_ids)
		response_dict = api.call()

		if 'status' in response_dict['responses']['GET_MAP_OBJECTS']:
			if response_dict['responses']['GET_MAP_OBJECTS']['status'] == 1:
			 	for map_cell in response_dict['responses']['GET_MAP_OBJECTS']['map_cells']:
			 		if 'wild_pokemons' in map_cell:
						for pokemon in map_cell['wild_pokemons']:
							poke = pokemon['pokemon_data']["pokemon_id"]
							print pokedex[poke-1]["name"], "at", pokemon["latitude"], ",", pokemon["longitude"]
							print "Hides at:", (datetime.datetime.now() + datetime.timedelta(milliseconds=pokemon["time_till_hidden_ms"])).time()

def main():
	
	config = load_config()

	pos = get_pos_by_name(config["loc"])

	api = PGoApi();
	api.set_position(*pos)

	if not api.login(config["auth"], config["username"], config["password"]):
		return

	find_pokemon(api, pos[0], pos[1])


main()