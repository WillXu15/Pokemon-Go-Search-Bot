import time
import datetime
import os
from slackclient import SlackClient
import sys

import pokemon
import pokedex

DEBUG = False;

pokedex = pokedex.import_pokedex()

sc = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
channel = os.environ.get('SLACK_CHANNEL_ID')

slack_start_time = datetime.datetime.now()


def main():
	if sc.rtm_connect():
		time_till_next_search = datetime.datetime.now() + datetime.timedelta(minutes=15)
		while True:
			if not parse(sc.rtm_read()):
				if datetime.datetime.now() > time_till_next_search:
					parse_pokemons(pokemon.find_pokemon_around_me())
					time_till_next_search = datetime.datetime.now() + datetime.timedelta(minutes=15)
			time.sleep(1)

	else:
		print "Connection Failed, invalid token?"

def parse_pokemons(pokemons):
	if pokemons == None:
		sc.api_call("chat.postMessage", as_user="true", channel=channel, text="unable to log in")
		return

	for pokemon in pokemons:
		print pokemon
		poke = pokedex[pokemon["pokemon_data"]["pokemon_id"] - 1]["name"]
		spotted = "{} spotted at {}, {} will hide at {}".format(poke.encode('utf-8'), pokemon["latitude"], pokemon["longitude"], (datetime.datetime.now() + datetime.timedelta(milliseconds=pokemon["time_till_hidden_ms"])).time())
		sc.api_call("chat.postMessage", as_user="true", channel=channel, text=spotted)


def parse(values):
	if len(values) > 0 and DEBUG:
		print values

	if values and len(values) > 0:
		for val in values:
			if val and 'text' in val and 'ts' in val:
				if datetime.datetime.fromtimestamp(float(val["ts"])) < slack_start_time:
					continue
				if 'search' in val['text']:
					sc.api_call("chat.postMessage", as_user="true", channel=channel, text="looking for pokemon")
					parse_pokemons(pokemon.find_pokemon_around_me())
		return True

	return False

if __name__ == "__main__":
	main()
