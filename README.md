# MongoDB basics
An introduction to MongoDB, its core components, and how it structures data using documents and collections.

## What is MongoDB?

MongoDB is a popular, open-source NoSQL database that uses a **document-oriented** data model. It stores data in flexible, JSON-like documents, making it well-suited for modern web and mobile applications with evolving data requirements.

Unlike traditional relational databases, MongoDB doesn't rely on tables and rows; instead, it uses **collections of documents**, offering greater flexibility and scalability.

## Documents and Collections

### Documents

Documents are the basic units of data in MongoDB. Each document is a **JSON-like** (BSON) object that stores data as key-value pairs. A document can include:

- Strings, numbers, booleans
- Arrays
- Embedded/nested documents
- Dates and more

Example:

```json
{
  "name": "Alice",
  "age": 30,
  "email": "alice@example.com",
  "skills": ["Python", "MongoDB"],
  "address": {
    "city": "Bristol",
    "postcode": "BS1 4DJ"
  }
}
```

Documents within the same collection can have different structures, making MongoDB very flexible.


### Collections

A **collection** is a group of related documents — similar to a table in a relational database, but without enforced structure. Collections organise documents within a MongoDB database and allow for efficient querying.

Key characteristics:
- Collections store multiple documents
- Documents within a collection can have different fields and data types
- No need to define a schema before inserting data

For example, a `users` collection might contain all user profile documents in an application:


```json
[
  {
    "name": "Alice",
    "email": "alice@example.com"
  },
  {
    "username": "bob42",
    "joined": "2023-07-01",
    "isActive": true
  }
]
```


## MongoDB Architecture

### What are Replica Sets?
Replica Sets are groups of MongoDB servers that maintain the same data, providing redundancy and high availability.

### How do they work?

- One primary node receives all write operations.
- Multiple secondary nodes replicate data from the primary asynchronously.
- If the primary fails, an election process promotes a secondary to primary, ensuring continued availability.


<div align="center">
  <img src="./Replica_Sets.png" alt="Replica Set Diagram" width="400" style="display: block; margin: auto;" />
</div>

### Advantages and Disadvantages

| Advantages                      | Disadvantages                  |
| -------------------------------| ------------------------------|
| High availability and redundancy | Replication lag possible       |
| Automatic failover              | More complex to manage         |
| Data durability                | Increased resource usage       |


### What is Sharding?

Sharding is MongoDB’s method of horizontally scaling by distributing data across multiple servers (shards).

### How does it work in MongoDB specifically?

- Data is partitioned using a shard key.
- Each shard holds a subset of the data.
- A query router (mongos) directs operations to the appropriate shard(s).
- Balancer process redistributes data to maintain an even load.

<div align="center">
  <img src="./Sharding.png" alt="Sharding Diagram" width="400" style="display: block; margin: auto;" />
</div>

### Advantages and Disadvantages

| Advantages                     | Disadvantages                   |
| ------------------------------| -------------------------------|
| Scales data across many servers | Shard key selection is critical |
| Handles large data volumes     | Increased operational complexity |
| Supports high throughput       | Some queries can be slower if not shard-key targeted |


## MongoDB Commands

#### 1. Basic MongoDB Shell Commands

Switch to or create a database:
```js
use starwars
```

Create a collection:
```js
db.createCollection("characters")
```

#### 2. Inserting Data
Insert one document:
```js
db.characters.insertOne({
  name: "Luke Skywalker",
  species: "Human",
  height: "172",
  mass: "77",
  gender: "male",
  eye_color: "blue"
})
```

Insert many documents:
```js
db.characters.insertMany([
  { name: "Leia Organa", species: "Human", height: "150", mass: "49", gender: "female", eye_color: "brown" },
  { name: "Chewbacca", species: "Wookiee", height: "228", mass: "112", gender: "male", eye_color: "blue" }
])
```

#### 3. Query Documents

Find all:
```js
db.characters.find()
```

*.find() vs .find({})*
- Both return all documents in the collection.

- .find({}) is explicitly saying “find everything with no filter”.

Filter results:
```js
db.characters.find({gender: "female"})
```
Show specific fields only:
```js
db.characters.find(
  { gender: "female" },
  { name: 1, eye_color: 1, _id: 0 }
)
```

#### 4. Updating Data
Update One:
```js

db.characters.updateOne(
  { name: "Chewbacca" },
  { $set: { mass: "1,358" } }
)
```
Remove a Field:
```js
db.characters.updateMany(
  { mass: "unknown" },
  { $unset: { mass: "" } }
)
```
Convert Mass to a Number:
```js
db.characters.updateMany(
  { mass: { $exists: true } },
  [ { $set: { mass: { $toDouble: "$mass" } } } ]
)
```

#### 5. Aggregation
##### What is aggregation?
The .aggregate() method lets you build a data pipeline, processing documents through multiple stages. It’s like combining filtering, grouping, sorting, and transforming in one command.

##### Structure
```js
db.collection.aggregate([
  { /* stage 1 */ },
  { /* stage 2 */ },
  ...
])
```
Each stage processes the documents before passing them to the next.

##### Common Stages

- $match – Filters documents (like .find())
```js
{ $match: { gender: "female" } }
```

- $group – Group by a field and do calculations

```js
{
  $group: {
    _id: "$species",
    averageMass: { $avg: "$mass" },
    count: { $sum: 1 }
  }
}
```

- $sort – Sort results
```js
{ $sort: { averageMass: 1 } }
```

- $project – Show or hide fields
```js
{ $project: { name: 1, height: 1, _id: 0 } }
```

- $addFields – Add new or calculated fields
```js
{
  $addFields: {
    heightInt: { $toInt: "$height" }
  }
}
```

- $expr – Use expressions (like $gt) on fields
Used inside $match when filtering based on calculated values.


##### Example: Average Mass and Count per Species
```js
db.characters.aggregate([
  {
    $match: {
      mass: { $ne: null },
      species: { $ne: null }
    }
  },
  {
    $group: {
      _id: "$species",
      averageMass: { $avg: "$mass" },
      count: { $sum: 1 }
    }
  },
  {
    $sort: { averageMass: 1 }
  }
])
```

**Explanation**:
- $match – Excludes documents missing mass or species

- $group – Groups by species, calculates average mass and counts

- $sort – Sorts species from lightest to heaviest

#### 6. List Collections in a Database

Get collection names only:
```js
db.getCollectionNames()
```
Get detailed info:
```js
db.getCollectionInfos()
```

#### 7. Advanced Filtering with Conversion
Find Characters Taller Than 200 (Exclude "unknown")
```js
db.characters.find(
  {
    $expr: {
      $gt: [
        {
          $convert: {
            input: "$height",
            to: "int",
            onError: null
          }
        },
        200
      ]
    }
  },
  {
    name: 1,
    height: 1,
    _id: 0
  }
)
```



### MongoDB Operator Summary

#### Comparison Operators

| Operator     | Meaning                                      | Example Use                                    |
|--------------|----------------------------------------------|------------------------------------------------|
| `$gt`        | Greater than                                 | `{ height: { $gt: 180 } }`                     |
| `$gte`       | Greater than or equal                        | `{ height: { $gte: 180 } }`                    |
| `$lt`        | Less than                                    | `{ height: { $lt: 180 } }`                     |
| `$lte`       | Less than or equal                           | `{ height: { $lte: 180 } }`                    |
| `$eq`        | Equals                                        | `{ eye_color: { $eq: "blue" } }`               |
| `$ne`        | Not equal                                     | `{ eye_color: { $ne: "unknown" } }`            |
| `$in`        | Value is in a given array                     | `{ species: { $in: ["Human", "Wookiee"] } }`   |
| `$nin`       | Value is **not** in a given array             | `{ species: { $nin: ["Droid", "unknown"] } }`  |

#### Aggregation Stages

| Stage         | Description                                                               |
|---------------|---------------------------------------------------------------------------|
| `$match`      | Filters documents like `.find()`                                          |
| `$group`      | Groups data by a field and performs calculations (e.g., count, avg)       |
| `$sort`       | Sorts documents (1 for ascending, -1 for descending)                      |
| `$project`    | Selects or reshapes which fields to return                                |
| `$addFields`  | Adds new fields or calculated values                                      |
| `$unset`      | Removes a field                                                           |
| `$limit`      | Limits number of documents returned                                       |
| `$skip`       | Skips a number of documents (used for pagination)                         |

#### Update Operators

| Operator     | Description                                         | Example                                        |
|--------------|-----------------------------------------------------|------------------------------------------------|
| `$set`       | Sets the value of a field                           | `{ $set: { mass: "100" } }`                    |
| `$unset`     | Removes a field from the document                   | `{ $unset: { mass: "" } }`                     |
| `$inc`       | Increments a field by a given value                 | `{ $inc: { age: 1 } }`                         |

#### Conversion & Logic

| Operator       | Description                                                     | Example                                          |
|----------------|-----------------------------------------------------------------|--------------------------------------------------|
| `$toInt`       | Converts a field to an integer                                  | `{ $toInt: "$height" }`                         |
| `$toDouble`    | Converts a field to a double (decimal)                          | `{ $toDouble: "$mass" }`                        |
| `$convert`     | Flexible conversion with `onError` or `onNull` options          | See filtering section                           |
| `$cond`        | "If this, then that, else..." logic                             | `{ $cond: { if: ..., then: ..., else: ... } }`  |
| `$expr`        | Enables use of operators in `.find()` filtering                 | `{ $expr: { $gt: [...] } }`                     |