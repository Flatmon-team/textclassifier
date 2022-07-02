import random
import requests
from typing import Any, Dict

from bson.objectid import ObjectId

from typing import Any, Optional
from dataclasses import dataclass, field

from db import db


@dataclass
class Tag:
    id: str
    name: str
    type: type
    filters: Dict[str, Any] = field(default=dict)


@dataclass
class Item:
    meta: Any
    tag: Tag


TAGS_LIST = [
    # Tag(
    #     id="is_rent",
    #     name="Аренда",
    #     type=bool,
    # ),
    # Tag(
    #     id="is_rent_short",
    #     name="Короткая аренда",
    #     type=bool,
    # ),
    # Tag(
    #     id="is_office",
    #     name="Офис",
    #     type=bool,
    # ),
    Tag(
        id="price_rent",
        name="Цена аренды",
        type=int,
        filters={"is_rent": True},
    ),
]

TAGS = {tag.id: tag for tag in TAGS_LIST}


def get_next() -> Optional[Item]:
    for tag in TAGS_LIST:
        metas = db.meta.find({tag.id: {"$exists": False}, **tag.filters})
        metas = list(metas)

        if not metas:
            return None

        return Item(meta=metas[0], tag=tag)

        #
        # random.shuffle(metas)

        # meta = metas[0]
        # return Item(meta=meta, tag=tag)

        # metas = db.meta.find({tag.id: {"$exists": False}, 'is_rent': True})
        # return Item(meta=meta, tag=tag)


        metas_scores = []

        for meta in metas:
            scores = requests.post(
                "http://localhost:8080",
                data=meta["data"].encode()
            ).json()
            scores = {bool(int(k)): v for k, v in scores.items()}
            metas_scores.append(scores[False])

        best = min(metas_scores)
        best_index = metas_scores.index(best)

        print(best)
        meta = metas[best_index]
        return Item(meta=meta, tag=tag)


def save_answer(raw_id: str, tag_id: str, value:str):
    tag = TAGS[tag_id]

    if value == "null":
        answer = None
    elif tag.type == bool:
        answer = bool(int(value))
    elif tag.type == int:
        answer = int(value)
    else:
        raise ValueError

    db.meta.update_one(
        {
            "raw_id": ObjectId(raw_id),
        }, {
            "$set": {tag_id: answer},
        },
    )
