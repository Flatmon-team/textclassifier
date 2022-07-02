from bson.objectid import ObjectId

from db import db
from filters import get_price


metas = db.meta.find({"price_rent": {"$exists": True}})
metas = list(metas)

correct = 0
for meta in metas:
    if get_price(meta["data"]) == meta["price_rent"]:
        correct += 1
    else:
        print("===============")
        print(meta["_id"], meta["price_rent"], get_price(meta["data"]))
        print(meta["data"])
        print("===============")

print(int(float(correct) / len(metas) * 100))
