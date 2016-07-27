import time
import datetime
import os
from slackclient import SlackClient

import pokemon
import pokedex


pokedex = pokedex.import_pokedex()
sc = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
channel = os.environ.get('SLACK_CHANNEL_ID')
time_start = datetime.datetime.now()

def main():
	if sc.rtm_connect():
		while True:
			pokemons = parse(sc.rtm_read())
			time.sleep(1)

	else:
		print "Connection Failed, invalid token?"

def parse_pokemons(pokemons):
	for pokemon in pokemons:
		print pokemon
		poke = pokedex[pokemon["pokemon_data"]["pokemon_id"] - 1]["name"]
		spotted = "{} spotted at {}, {} will hide at {}".format(poke.encode('utf-8'), pokemon["latitude"], pokemon["longitude"], (datetime.datetime.now() + datetime.timedelta(milliseconds=pokemon["time_till_hidden_ms"])).time())
		sc.api_call("chat.postMessage", as_user="true", channel=channel, text=spotted)


def parse(values):
	if len(values) > 0:
		print values

	if values and len(values) > 0:
		for val in values:
			if val and 'text' in val and 'ts' in val:
				if datetime.datetime.fromtimestamp(float(val["ts"])) < time_start:
					continue
				if 'search' in val['text']:
					print sc.api_call("chat.postMessage", as_user="true", channel=channel, text="looking for pokemon")
					parse_pokemons(pokemon.find_pokemon_around_me())


if __name__ == "__main__":
	main()
