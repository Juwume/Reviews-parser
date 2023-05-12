import flask
from src import app
from src.scripts.parse_wb import download_wildberries_comments
from src.scripts.parse_mirkorma import download_mirkorma_comments
from src.scripts.parse_petshop import download_petshop_comments
from src.utils import connect_mongo, check_query_in_db
from src.models.wb import ProductWB, QueryWB
from src.models.mirkorma import ProductMirkorma, QueryMirkorma
from src.models.petshop import ProductPetshop, QueryPetshop
from datetime import datetime
import json
from bson import json_util
from flask import request


@app.route("/")
def index():
    return {"message": "Hello, this is my diploma work"}


@app.route("/api/wb/<string:query>", methods=["GET"])
async def parse_wb(query):
    date_start = datetime.strptime(
        request.args.get("date_start", "2000-01-01"), "%Y-%m-%d"
    )
    date_end = datetime.strptime(request.args.get("date_end", "2025-01-01"), "%Y-%m-%d")
    connect_mongo("WILDBERRIES")
    is_in_db = check_query_in_db(query, QueryWB, date_end)
    # Если в базе не было такого запроса
    if is_in_db == "Not found":
        products = await download_wildberries_comments(query)
        QueryWB(
            query=query,
            timestamp=datetime.now(),
            products=products,
        ).save()
    # Если был запрос, но слишком давно
    elif is_in_db == "Time":
        products = await download_wildberries_comments(query)
        found = QueryWB.objects(query=query).get()
        # Обновление QueryPetshop новыми данными
        found.products = products
        found.timestamp = datetime.now()
        found.save()
    ids = QueryWB.objects(query=query).only("products").get().products
    # Выборка комментариев по нужным датам
    res = ProductWB.objects().aggregate(
        [
            {"$match": {"id_product": {"$in": ids}}},
            {"$match": {"comments.date": {"$gte": date_start, "$lte": date_end}}},
            {
                "$project": {
                    "_id": 0,
                    "name": 1,
                    "description": 1,
                    "seller": 1,
                    "category_name": 1,
                    "brand": 1,
                    "price": 1,
                    "url": 1,
                    "comments": {
                        "$filter": {
                            "input": "$comments",
                            "as": "comment",
                            "cond": {
                                "$and": [
                                    {"$gte": ["$$comment.date", date_start]},
                                    {"$lte": ["$$comment.date", date_end]},
                                ]
                            },
                        }
                    },
                }
            },
        ]
    )

    return json.dumps([doc for doc in res], default=json_util.default)


@app.route("/api/mirkorma/<string:query>", methods=["GET"])
async def parse_mirkorma(query):
    # TODO: Довести до ума (можно в последнюю очередь)
    connect_mongo("MIRKORMA")
    # is_in_db = check_query_in_db(query, QueryMirkorma)
    # if not is_in_db:
    products = await download_mirkorma_comments(query)
    return [product.to_json() for product in products]
    # return ProductMirkorma.objects().to_json()


@app.route("/api/petshop/<string:query>", methods=["GET"])
async def parse_petshop(query):
    # Get params
    date_start = datetime.strptime(
        request.args.get("date_start", "2000-01-01"), "%Y-%m-%d"
    )
    date_end = datetime.strptime(request.args.get("date_end", "2025-01-01"), "%Y-%m-%d")
    # Connection to database and search query
    connect_mongo("PETSHOP")
    is_in_db = check_query_in_db(query, QueryPetshop, date_end)

    # Если в базе не было такого запроса
    if is_in_db == "Not found":
        products = await download_petshop_comments(query)
        QueryPetshop(
            query=query,
            timestamp=datetime.now(),
            products=products,
        ).save()

    # Если был запрос, но слишком давно
    elif is_in_db == "Time":
        products = await download_petshop_comments(query)
        found = QueryPetshop.objects(query=query).get()
        # Обновление QueryPetshop новыми данными
        found.products = products
        found.timestamp = datetime.now()
        found.save()

    ids = QueryPetshop.objects(query=query).only("products").get().products
    # Выборка комментариев по нужным датам
    res = ProductPetshop.objects().aggregate(
        [
            {"$match": {"id_product": {"$in": ids}}},
            {"$match": {"comments.date": {"$gte": date_start, "$lte": date_end}}},
            {
                "$project": {
                    "_id": 0,
                    "id_product": 1,
                    "id_similar_products": 1,
                    "name": 1,
                    "description": 1,
                    "category_id": 1,
                    "category_name": 1,
                    "brand": 1,
                    "price": 1,
                    "url": 1,
                    "is_available": 1,
                    "comments": {
                        "$filter": {
                            "input": "$comments",
                            "as": "comment",
                            "cond": {
                                "$and": [
                                    {"$gte": ["$$comment.date", date_start]},
                                    {"$lte": ["$$comment.date", date_end]},
                                ]
                            },
                        }
                    },
                }
            },
        ]
    )

    return json.dumps([doc for doc in res], default=json_util.default)


@app.route("/healthcheck", methods=["GET"])
async def get_healthcheck():
    return flask.Response(status=200)
