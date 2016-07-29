import json
import datetime
import os
import logging

import utils

from pgoapi import PGoApi
from pgoapi import utilities as pgoutil

from google.protobuf.internal import encoder
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

class PokemonSearch:
	def __init__(self):
		self.api = PGoApi()
		self.load_config()
		self.pos = get_pos_by_name(self.config["loc"])
		self.api.set_position(*self.pos)

	def load_config(self):
		filename = 'config.json'
		dirname = os.path.dirname(os.path.realpath(__file__))
		with open(os.path.join(dirname, filename)) as config_file:
			self.config = json.load(config_file)

	def set_location(self, lat, lng):
		self.pos = (float(lat), float(lng), 0)
		self.api.set_position(*self.pos)
		
	def find_pokemon_around_me(self):
		print self.pos
		try:
			if not self.api.login(self.config["auth"], self.config["username"], self.config["password"]):
				return None
		except Exception:
			print "error logging in"
			return None

		return self.find_pokemon()
	
	def find_pokemon(self):
		step_size = 0.0015
		step_limit = 16
		coords = utils.generate_spiral(self.pos[0], self.pos[1], step_size, step_limit)

		pokemons = []
		for coord in coords:
			lat = coord["lat"]
			lng = coord["lng"]

			self.api.set_position(lat, lng, 0)
			cell_ids = get_cell_ids(lat, lng)
			timestamps = [0,] * len(cell_ids)

			self.api.get_map_objects(latitude = pgoutil.f2i(lat), longitude = pgoutil.f2i(lng), since_timestamp_ms = timestamps, cell_id = cell_ids)
			response_dict = self.api.call()

			if 'GET_MAP_OBJECTS' in response_dict['responses']:
				if 'status' in response_dict['responses']['GET_MAP_OBJECTS']:
					if response_dict['responses']['GET_MAP_OBJECTS']['status'] == 1:
					 	for map_cell in response_dict['responses']['GET_MAP_OBJECTS']['map_cells']:
					 		if 'wild_pokemons' in map_cell:
								for pokemon in map_cell['wild_pokemons']:
									pokemons.append(pokemon)
		
		return {v['encounter_id']:v for v in pokemons}.values()


def main():
	pokemon = PokemonSearch()
	print pokemon.find_pokemon_around_me()

if __name__ == '__main__':
    main()
