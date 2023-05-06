import flask
import mongoengine
from src import app
from src.scripts.parse_wb import download_wildberries_comments
from src.scripts.parse_mirkorma import download_mirkorma_comments
from src.scripts.parse_petshop import download_petshop_products
from src.utils import connect_mongo, check_query_in_db
from src.models.wb import ProductWB, QueryWB
from src.models.mirkorma import ProductMirkorma, QueryMirkorma
from src.models.petshop import ProductPetshop, QueryPetshop, ProductPetshopEmbedded
from datetime import datetime
import json
from bson import json_util

from flask import request


@app.route("/")
def index():
    return {"message": "Hello, this is my diploma work"}


@app.route("/api/wb/<string:query>", methods=["GET"])
async def parse_wb(query):
    # TODO: Добавить кэш запроса, добавить селекцию по дате
    # TODO: Добавить прокси
    connect_mongo("WILDBERRIES")
    is_in_db = check_query_in_db(query, QueryWB)
    if not is_in_db:
        products = await download_wildberries_comments(query)
        return [product.to_json() for product in products]
    return ProductWB.objects().to_json()
    # return products
    # download_wildberries_products()


@app.route("/api/wb/get_data", methods=["GET"])
def get_data_wb():
    filters = {}
    if request.args.get("seller"):
        filters["seller"] = request.args.get("seller")
    else:
        filters["seller"] = ""
    if request.args.get("date"):
        filters["date"] = request.args.get("date")
    else:
        filters["date"] = "01.01.1900"
    if request.args.get("brand"):
        filters["brand"] = request.args.get("brand")
    else:
        filters["brand"] = ""
    connect_mongo("WILDBERRIES")
    print(
        ProductWB.objects(
            brand__istartswith=filters["brand"], seller__istartswith=filters["seller"]
        ).to_json()
    )
    return flask.Response(status=200)


@app.route("/get_data", methods=["GET"])
def get_data():
    time_start = datetime.strptime(request.args.get("time_start"), '%Y-%m-%d')
    time_end = request.args.get("time_end")
    connect_mongo("PETSHOP")
    # res = ProductPetshop.objects().aggregate(
    #     {"$match": {"comments.date": {"$gte": time_start}}},
    #     {"$unwind": "$comments"},
    #     {"$group": {"_id": '$name', "comments": {"$push": '$comments.date'}}}
    # )
    res = ProductPetshop.objects().aggregate(
        {'$match': {}}
    )
    out = [doc for doc in res]
    json_result = json.dumps(out, default=json_util.default)
    print(out)
    return json_result


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
    # TODO: Доделать селекцию по дате
    time_start = request.args.get("time_start")
    time_end = request.args.get("time_end")
    connect_mongo("PETSHOP")
    is_in_db = check_query_in_db(query, QueryPetshop)
    # Если в базе не было такого запроса
    if is_in_db == "Not found":
        products = await download_petshop_products(query)
        # Исправление JSON
        for idx, product in enumerate(products):
            products[idx] = json.loads(product.to_json())
            products[idx].pop("_id", None)
            # Дата конвертируется неправильно, поэтому поправляем
            for comment in products[idx]['comments']:
                comment['date'] = datetime.fromtimestamp(comment['date']['$date'] / 1000)
        QueryPetshop(query=query, timestamp=datetime.now(), products=products).save()
        return products
    # Если был запрос, но слишком давно
    elif is_in_db == "Time":
        products = await download_petshop_products(query)
        found = QueryPetshop.objects(query=query).get()
        # Исправление JSON
        for idx, product in enumerate(products):
            products[idx] = json.loads(product.to_json())
            products[idx].pop("_id", None)
            # Дата конвертируется неправильно, поэтому поправляем
            for comment in products[idx]['comments']:
                comment['date'] = datetime.fromtimestamp(
                    comment['date']['$date'] / 1000)
        found.products = [
            ProductPetshopEmbedded(
                id_product=product["id_product"],
                id_similar_products=product["id_similar_products"],
                name=product["name"],
                description=product["description"],
                category_id=product["category_id"],
                category_name=product["category_name"],
                brand=product["brand"],
                price=product["price"],
                price_regional=product.get("price_regional"),
                price_old=product.get("price_old"),
                url=product["url"],
                is_available=product["is_available"],
                comments=product["comments"],
            )
            for product in products
        ]
        found.timestamp = datetime.now()
        found.save()
        return products
    return QueryPetshop.objects(query=query).to_json()


@app.route("/healthcheck", methods=["GET"])
async def get_healthcheck():
    return flask.Response(status=200)
