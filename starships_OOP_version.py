import pymongo
import requests


class StarWarsDataManager:
    def __init__(self, db_name="starwars"):
        self.client = pymongo.MongoClient()
        self.db = self.client[db_name]
        self.characters_collection = self.db['characters']
        self.starships_collection = self.db['starships']

    def repopulate_characters(self):
        self.characters_collection.drop()
        url = "https://swapi.tech/api/people"
        characters = []

        while url:
            response = requests.get(url).json()
            for result in response['results']:
                person_url = result['url']
                full_data = requests.get(person_url).json()['result']
                char = full_data['properties']
                char['url'] = person_url
                characters.append(char)
            url = response.get('next')

        self.characters_collection.insert_many(characters)
        print(f"Inserted {len(characters)} characters.")

    def get_all_starships(self):
        starships = []
        url = "https://swapi.tech/api/starships"

        while url:
            response = requests.get(url).json()
            starships.extend(response['results'])
            url = response.get('next')

        return starships

    def get_full_starship_data(self, starships):
        full_data = []
        for ship in starships:
            ship_url = ship['url']
            response = requests.get(ship_url).json()
            full_data.append(response['result']['properties'])
        return full_data

    def map_pilot_urls_to_object_ids(self, pilot_urls):
        object_ids = []
        for url in pilot_urls:
            char_doc = self.characters_collection.find_one({"url": url})
            if char_doc:
                object_ids.append(char_doc['_id'])
        return object_ids

    def prepare_and_insert_starships(self):
        starships = self.get_all_starships()
        full_data = self.get_full_starship_data(starships)

        self.starships_collection.drop()

        for ship in full_data:
            pilots = ship.get('pilots', [])
            ship['pilots'] = self.map_pilot_urls_to_object_ids(pilots)
            self.starships_collection.insert_one(ship)

        print(f"Inserted {len(full_data)} starships.")

    def show_starships_summary(self):
        print("Starships summary:")
        for s in self.starships_collection.find({}, {"name": 1, "cost_in_credits": 1, "pilots": 1, "_id": 0}):
            print(s)
        print(f"\n Total starships: {self.starships_collection.count_documents({})}")

    def show_sample_character(self):
        print("\n Sample character:")
        print(self.characters_collection.find_one())


if __name__ == "__main__":
    sw = StarWarsDataManager()

    sw.repopulate_characters()
    sw.prepare_and_insert_starships()

    sw.show_starships_summary()
    sw.show_sample_character()
