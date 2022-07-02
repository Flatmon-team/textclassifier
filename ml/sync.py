from db import db
from filters import CHATS

import hashlib


def delete_duplicates():
    hashes = set()

    deleted_count = 0

    for m in db.meta.find():
        hash = hashlib.md5(m["data"].strip().encode()).hexdigest()
        if hash in hashes:
            deleted_count += 1
            db.meta.delete_one({"_id": m["_id"]})
        else:
            hashes.add(hash)

    print(f"Deleted {deleted_count} items")


def main():
    existed_ids = [
        m["raw_id"]
        for m in db.meta.find({}, {"raw_id": 1})
    ]
    messages = db.messages.find(
        {
            "_id": {"$nin": existed_ids},
            "raw.chat.id": {"$in": list(CHATS)},
            "$or": [{"raw.text": {"$exists": True}}, {"raw.caption": {"$exists": True}}]
        })

    count_added = 0
    for message in messages:
        raw = message["raw"]

        text = raw.get("text") or raw.get("caption")
        if not text:
            continue

        db.meta.insert_one({
            "raw_id": message["_id"],
            "data": text,
        })
        count_added += 1

    print(f"Added {count_added} items")

    delete_duplicates()


if __name__ == "__main__":
    main()
