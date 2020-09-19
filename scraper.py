#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
This module scrapes Serebii.net for Pokémon statistics.
"""
import argparse
import json
import logging
import bs4
import requests
import re
import html5lib

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

OUTPUT_FILE = 'pokemon.json'
ROOT_URL = "https://serebii.net"

PARSER = argparse.ArgumentParser(description='A Pokémon web scraper')
PARSER.add_argument('-s', '--save', action='store_true',
                    help='save the output to JSON')
PARSER.add_argument('-f', '--first', default=1, type=int,
                    help='the number of the first Pokémon to retrieve')
PARSER.add_argument('-l', '--last', default=1, type=int,
                    help='the number of the last Pokémon to retrieve')
PARSER.add_argument('-v', '--verbose', action='store_true',
                    help='print the Pokémon\'s statistics to console')
ARGS = PARSER.parse_args()


def get_pokemon(urls):
    pokemon_list = []

    for url in urls:
        LOGGER.info('Extracting data from Serebii.net url {}'.format(ROOT_URL+url))
        data = requests.get(ROOT_URL+url)
        soup = bs4.BeautifulSoup(data.text, 'html5lib')
        try:
            pokemon = get_pokemon_data(soup)
        except Exception:
            LOGGER.error('Skipping pokemon with url {}'.format(url))

        if not ARGS.save or ARGS.verbose:
            print_pokemon_data(pokemon)
            LOGGER.info('Adding %s %s to dataset', pokemon['number'], pokemon['name'])
            pokemon_list.append(pokemon)

    if ARGS.save:
        LOGGER.info('Saving to %s', OUTPUT_FILE)
        save_to_json(pokemon_list)
    else:
        LOGGER.info( 'All Pokémon retrieved! To save to JSON, use the --save flag')


def get_pokemon_data(pokemonSoup):
    try:
        dextables = pokemonSoup.select('table[class="dextable"]')
        pokemon_info = dextables[1].select('td[class="fooinfo"]')


        pokemon = dict()
        pokemon['name'] =              pokemon_info[0].text
        pokemon['number'] =            pokemon_info[2].select('td')[1].text
        pokemon['classification'] =    pokemon_info[4].text
        pokemon['height'] =            (pokemon_info[5].text).split('\r\n\t\t\t')
        pokemon['weight'] =            (pokemon_info[6].text).split('\r\n\t\t\t')

        try:
            base_stats = pokemonSoup.find('td', text=re.compile("Base Stats - Total:.*")).parent.select('td[class="fooinfo"]')
        except Exception:
            LOGGER.error('There was an error trying to identify HTML elements on the webpage.')

        pokemon['hit_points'] = int(base_stats[1].text)
        pokemon['attack'] = int(base_stats[2].text)
        pokemon['defense'] = int(base_stats[3].text)
        pokemon['special'] = int(base_stats[4].text)
        pokemon['speed'] = int(base_stats[5].text)

    except Exception:
        LOGGER.error(
            'There was an error trying to identify HTML elements on the webpage.')
        raise

    return pokemon

def save_to_json(pokemon_list):
    """
    Save Pokémon array to JSON file.
    :param pokemon_list: Array of Pokémon data.
    """
    with open(OUTPUT_FILE, mode='w', encoding='utf-8') as output_file:
        json.dump(pokemon_list, output_file, indent=4)


def print_pokemon_data(pokemon):
    """
    Print formatted Pokémon data.
    :param pokemon: Pokémon object containing statistics.
    """
    print('Name\t\t', pokemon['name'])
    print('Number\t\t', pokemon['number'])
    print('Classification\t', pokemon['classification'])
    print('Height\t\t', ' '.join(str(i) for i in pokemon['height']))
    print('Weight\t\t', ' '.join(str(i) for i in pokemon['weight']))
    print('HP\t\t', pokemon['hit_points'])
    print('Attack\t\t', pokemon['attack'])
    print('Defense\t\t', pokemon['defense'])
    print('Special\t\t', pokemon['special'])
    print('Speed\t\t', pokemon['speed'])


def getPokemonUrlsForPokedex():
    urls = None
    pokedex = requests.get(ROOT_URL+ '/pokedex-swsh')
    soup = bs4.BeautifulSoup(pokedex.text,'html5lib')
    urls = list(set([(opt.attrs['value']) for opt in soup.find_all('option',value=re.compile('^/pokedex-swsh/[a-z]*/$'))]))
    return urls

def test_method():
    soup = bs4.BeautifulSoup(open('test-hitmontop.html','r'),'html5lib')
    pokemon = get_pokemon_data(soup)
    print_pokemon_data(pokemon)

if __name__ == '__main__':
    try:
        urls = getPokemonUrlsForPokedex()
        get_pokemon(urls)
    except Exception as ex:
        LOGGER.error(ex)
        raise
