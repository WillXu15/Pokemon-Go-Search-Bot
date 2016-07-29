import time
import datetime
import os
import re

from slackclient import SlackClient
import sys

import pokemon
import pokedex

DEBUG = True;

pokedex = pokedex.import_pokedex()

sc = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
channel = os.environ.get('SLACK_CHANNEL_ID')
slack_bot_id = os.environ.get('SLACK_BOT_ID')
slack_start_time = datetime.datetime.now()

authorized_users = [os.environ.get('SLACK_AUTHORIZED_USER_ID')]

def main():
	if sc.rtm_connect():
		pokemon_search = pokemon.PokemonSearch()
		time_till_next_search = datetime.datetime.now() + datetime.timedelta(minutes=15)
		while True:
			if not parse(pokemon_search, sc.rtm_read()):
				if datetime.datetime.now() > time_till_next_search:
					parse_pokemons(pokemon_search.find_pokemon_around_me())
					time_till_next_search = datetime.datetime.now() + datetime.timedelta(minutes=15)
			time.sleep(1)

	else:
		print "Connection Failed, invalid token?"

def parse_pokemons(pokemons):
	sc.api_call("chat.postMessage", as_user="true", channel=channel, text="looking for pokemon")
	if pokemons == None:
		sc.api_call("chat.postMessage", as_user="true", channel=channel, text="unable to log in")
		return

	for pokemon in pokemons:
		print pokemon
		poke = pokedex[pokemon["pokemon_data"]["pokemon_id"] - 1]["name"]
		time_till_hidden = (datetime.datetime.now() + datetime.timedelta(milliseconds=pokemon["time_till_hidden_ms"])).time()
		spotted = "{} spotted <https://www.google.com/maps/dir//{},{}|here> will disappear at {}".format(poke.encode('utf-8'), pokemon["latitude"], pokemon["longitude"], time_till_hidden.strftime("%I:%M:%S"))
		sc.api_call("chat.postMessage", as_user="true", channel=channel, text=spotted)


def parse(pokemon_search, values):
	if len(values) > 0 and DEBUG:
		print values

	if values and len(values) > 0:
		for val in values:
			if val and 'text' in val and 'ts' in val:
				if 'user' in val and val['user'] == "":
					continue
				if 'user' in val and val['user'] not in authorized_users:
					sc.api_call("chat.postMessage", as_user="true", channel=channel, text="you are unauthorized to make that call")
					continue
				if datetime.datetime.fromtimestamp(float(val["ts"])) < slack_start_time:
					continue
				search_str = re.compile("^[sS]earch$").findall(val["text"])
				set_str = re.compile("^[sS]et").findall(val["text"])
				if search_str:
					parse_pokemons(pokemon_search.find_pokemon_around_me())
				if set_str:
					latlng = re.compile("-?\d+.\d+").findall(val["text"])
					if len(latlng) == 2:
						lat, lng = latlng
						pokemon_search.set_location(lat, lng)
						sc.api_call("chat.postMessage", as_user="true", channel=channel, text="location set")
					else:
						sc.api_call("chat.postMessage", as_user="true", channel=channel, text="wrong arguments")
		return True

	return False

if __name__ == "__main__":
	main()
