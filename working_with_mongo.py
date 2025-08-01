# Working with Mongodb in Python

#Importing pymongo
import pymongo

#Establish connection + Creating a database object
client = pymongo.MongoClient()
db = client['starwars']

# retrive a document from the db
luke = db.characters.find({"name": "Luke Skywalker"}) # Returns cursor obj
print(luke)

luke_not_object = db.characters.find_one({ "name": "Luke Skywalker" })  # does not wrap as cursor obj
print(luke_not_object)

# Multiple records

droids = db.characters.find({"species.name": "Droid"}) # Iterate through cursor obj
for droid in droids:
    print(droid["name"])



# Queries:
# 1
print(db.characters.find_one(
    {"name": "Darth Vader"},
    {"name": 1, "height": 1, "_id": 0}
)
)

# 2
for doc in db.characters.find({"eye_color": "yellow"}):
    print(doc["name"])

# 3
for man in db.characters.find({"gender": "male"}).limit(3):
    print(man)

# 4
for human in db.characters.find({"species.name": "Human", "homeworld.name": "Alderaan"}):
    print(human["name"])


### Aggregation Exercises

# What is the average height of all female characters
avg_female_height = db.characters.aggregate([
    {"$match": {"gender": "female"}},
    {"$group": {"_id": "$gender", "avg_height": {"$avg": "$height"}}}
])

# Our cursor contains 1 object
# We could iterate through, cast to a list, or use the next method
print(avg_female_height.next())


# Which character in the database is the tallest?
max_height = db.characters.aggregate([
    {"$group":
         {"_id": None, "max_height": {"$max": "$height"}}
    }
]).next()["max_height"]

# Looks nicer and helps if multiple people share the max height
for tallest in db.characters.find({"height": max_height}):
    print(tallest["name"], tallest["height"])