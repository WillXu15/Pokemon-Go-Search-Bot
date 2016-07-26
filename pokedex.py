import json

def import_pokedex():
	with open('pokedex.json') as pokedex:
		return json.load(pokedex)["pokemon"]