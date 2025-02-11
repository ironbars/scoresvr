import json
import os

from bson.objectid import ObjectId
from pymongo import InsertOne, MongoClient

MONGO_HOST = os.environ.get("SCORESVR_MONGO_HOST", "127.0.0.1")
MONGO_PORT = os.environ.get("SCORESVR_MONGO_PORT", "27017")

client = MongoClient(f"mongodb://{MONGO_HOST}:{MONGO_PORT}")
db = client.music
scollection = db.scores
ecollection = db.engravings
srequesting = []
erequesting = []

with open("scores.json", "r") as sstream:
    score_data = json.load(sstream)

with open("engravings.json", "r") as estream:
    engraving_data = json.load(estream)

scores = score_data["scores"]
engravings = engraving_data["engravings"]

for score in scores:
    score["_id"] = ObjectId(score["_id"])
    score["engraving_id"] = ObjectId(score["engraving_id"])

    srequesting.append(InsertOne(score))

for engraving in engravings:
    engraving["_id"] = ObjectId(engraving["_id"])
    engraving["score_id"] = ObjectId(engraving["score_id"])

    erequesting.append(InsertOne(engraving))

sresult = scollection.bulk_write(srequesting)
eresult = ecollection.bulk_write(erequesting)

client.close()
