import requests
import json
from model import Actor, Show
from typing import List

class TVMaze_API_Access:
    def __init__(self, url):
        self.url = url

    def get_json(self, url):
        resp = requests.get(url=url)
        data = resp.json()
        return data

    def get_actor(self, name) -> Actor:
        query_url = self.url + name
        print(query_url)
        # Fetch the query result to a json object
        json_obj = self.get_json(query_url)
        # Ensure the highest scored actor response exactly matches the queried actor name
        if str(json_obj[0]['person']['name']).lower() == name.lower():
            # Retrieve shows for the current actor
            shows_query_url = 'https://api.tvmaze.com/people/{}/castcredits'.format(json_obj[0]['person']['id'])
            shows_json_obj = self.get_json(shows_query_url)
            show_urls = map(lambda n: n['_links']['show']['href'], shows_json_obj)
            show_details = map(lambda n: self.get_json(n), show_urls)
            show_names = map(lambda n: n['name'], show_details)
            show_entities = []
            for show_name in show_names:
                existing_show = Show.find_by_showname(show_name)
                if existing_show is None:
                    show_entities.append(Show(name = show_name))
                else:
                    show_entities.append(existing_show)
            actor = Actor.from_json(json_obj[0]['person'])
            actor.shows = show_entities
            return actor
        else: 
            return None
        
