import pymongo
import requests

# Exercise:

# The data in this database (starwars) has been pulled from SWAPI Reborn - Star Wars APIs & Explorer.
# Note: The old api is no longer supported, there may be some differences between the data we have been working with
# and the data in this api.

# As well as 'people', the API has data on starships. In Python, pull data on all available starships from the API.
# The "pilots" key contains URLs pointing to the characters who pilot the starship.

# Use these to replace 'pilots' with a list of ObjectIDs from our characters collection, then insert the starships
# into their own collection. Use functions at the very least! OOP preferred.

# Establish connection
client = pymongo.MongoClient()
db = client['starwars']
characters_collection = db['characters']
starships_collection = db['starships']

# Repopulate characters
def repopulate_characters():
    characters_collection.drop()

    url = "https://swapi.tech/api/people"
    characters = []

    while url:
        response = requests.get(url).json()
        for result in response['results']:
            person_url = result['url']
            full_data = requests.get(person_url).json()['result']
            char = full_data['properties']
            char['url'] = person_url  # ✅ Needed for matching
            characters.append(char)
        url = response.get('next')

    characters_collection.insert_many(characters)
    print(f"Inserted {len(characters)} characters with URLs!")


# Get all starships from SWAPI Reborn
def get_all_starships():
    starships = []
    url = "https://swapi.tech/api/starships"

    while url:
        response = requests.get(url)
        data = response.json()
        starships.extend(data['results'])
        url = data.get('next')  # next page

    return starships

# Checks
ships = get_all_starships()
print(len(ships))
print(ships[0])


# Fetch full starship data
def get_full_starship_data(starships):
    full_data = []
    for ship in starships:
        ship_url = ship['url']
        response = requests.get(ship_url)
        full_data.append(response.json()['result']['properties'])
    return full_data

full_ships = get_full_starship_data(ships)
print(len(full_ships))       # Should match len(ships)
print(full_ships[0].keys())  # See what fields are in one full record
print(full_ships[0])         # View full details of the first starship


# Map pilot URLs to MongoDB ObjectIDs
def map_pilot_urls_to_object_ids(pilot_urls):
    object_ids = []
    for url in pilot_urls:
        char_doc = characters_collection.find_one({"url": url})
        if char_doc:
            object_ids.append(char_doc['_id'])
    return object_ids



# Clean and insert starship data

def prepare_and_insert_starships():
    starships = get_all_starships()
    full_data = get_full_starship_data(starships)

    starships_collection.drop()

    for ship in full_data:
        pilots = ship.get('pilots', [])
        object_ids = map_pilot_urls_to_object_ids(pilots)
        ship['pilots'] = object_ids

        starships_collection.insert_one(ship)

# Run
if __name__ == "__main__":
    repopulate_characters()
    prepare_and_insert_starships()
    print("Done inserting starships!")

    # Checks
    for s in starships_collection.find({}, {"name": 1, "cost_in_credits": 1, "pilots": 1, "_id": 0}):
        print(s)

print(starships_collection.count_documents({}))


print(characters_collection.find_one())


