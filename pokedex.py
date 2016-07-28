import json
import os

def import_pokedex():
    filename = 'pokedex.json'
    dirname = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dirname, filename)) as pokedex:
		return json.load(pokedex)["pokemon"]
