import json
import datetime
import time
import os
import logging

import utils

from pgoapi import PGoApi
from pgoapi import utilities as pgoutil

from google.protobuf.internal import encoder

log = logging.getLogger(__name__)

class PokemonSearch:
	def __init__(self):
		self.api = PGoApi()
		self.load_config()
		self.pos = utils.get_pos_by_name(self.config["loc"])
		self.api.set_position(*self.pos)
		self.logged_in = self.login()
		logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(module)10s] [%(levelname)5s] %(message)s', filename=".log")
		# log level for http request class
		logging.getLogger("requests").setLevel(logging.WARNING)
		# log level for main pgoapi class
		logging.getLogger("pgoapi").setLevel(logging.INFO)
		# log level for internal pgoapi class
		logging.getLogger("rpc_api").setLevel(logging.INFO)

	def login(self):
		return self.api.login(self.config["auth"], self.config['username'], self.config['password'])
	

	def load_config(self):
		filename = 'config.json'
		dirname = os.path.dirname(os.path.realpath(__file__))
		with open(os.path.join(dirname, filename)) as config_file:
			self.config = json.load(config_file)

	def set_location(self, lat, lng):
		self.pos = (float(lat), float(lng), 0)
		self.api.set_position(*self.pos)
		
	def find_pokemon_around_me(self):
		return self.find_pokemon()
	
	def find_pokemon(self):
		step_size = 0.0015
		step_limit = 16
		coords = utils.generate_spiral(self.pos[0], self.pos[1], step_size, step_limit)

		pokemons = []
		for coord in coords:
			time.sleep(5)
			lat = coord["lat"]
			lng = coord["lng"]

			self.api.set_position(lat, lng, 0)
			cell_ids = utils.get_cell_ids(lat, lng)
			timestamps = [0,] * len(cell_ids)

			response_dict = self.api.get_map_objects(latitude = pgoutil.f2i(lat), longitude = pgoutil.f2i(lng), since_timestamp_ms = timestamps, cell_id = cell_ids)
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
	pokemon.set_location(39.6941436, -75.64809070000001)
	print pokemon.find_pokemon()

if __name__ == '__main__':
    main()
