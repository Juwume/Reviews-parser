import flask
from src import app
from src.scripts.parse_wb import download_wildberries_comments
from src.scripts.parse_mirkorma import download_mirkorma_comments
from src.scripts.parse_petshop import download_petshop_products
from src.utils import connect_mongo, check_query_in_db
from src.models.wb import ProductWB, QueryWB
from src.models.mirkorma import ProductMirkorma, QueryMirkorma

from flask import request


@app.route('/')
def index():
    return {'message': 'Hello, this is my diploma work'}


@app.route('/api/wb/<string:query>', methods=['GET'])
async def parse_wb(query):
    connect_mongo('WILDBERRIES')
    is_in_db = check_query_in_db(query, QueryWB)
    if not is_in_db:
        products = await download_wildberries_comments(query)
        return [product.to_json() for product in products]
    return ProductWB.objects().to_json()
    # return products
    # download_wildberries_products()
@app.route('/api/wb/get_data', methods=['GET'])
def get_data_wb():
    filters = {}
    if request.args.get('seller'):
        filters['seller'] = request.args.get('seller')
    else:
        filters['seller'] = ''
    if request.args.get('date'):
        filters['date'] = request.args.get('date')
    else:
        filters['date'] = '01.01.1900'
    if request.args.get('brand'):
        filters['brand'] = request.args.get('brand')
    else:
        filters['brand'] = ''
    connect_mongo('WILDBERRIES')
    print(ProductWB.objects(
        brand__istartswith=filters['brand'],
        seller__istartswith=filters['seller']
    ).to_json())
    return flask.Response(status=200)

@app.route('/get_data', methods=['GET'])
def get_data():
    connector = connect_mongo('wildberries')
    print('--------')
    print(list(connector['products'].find()))
    print('--------')
    return flask.Response(status=200)


@app.route('/api/mirkorma/<string:query>', methods=['GET'])
async def parse_mirkorma(query):
    connect_mongo('MIRKORMA')
    # is_in_db = check_query_in_db(query, QueryMirkorma)
    # if not is_in_db:
    products = await download_mirkorma_comments(query)
    return [product.to_json() for product in products]
    # return ProductMirkorma.objects().to_json()


@app.route('/api/petshop/<string:query>', methods=['GET'])
async def parse_petshop(query):
    connect_mongo('PETSHOP')
    # is_in_db = check_query_in_db(query, QueryMirkorma)
    # if not is_in_db:
    products = await download_petshop_products(query)
    return [product.to_json() for product in products]
    # return ProductMirkorma.objects().to_json()


@app.route('/healthcheck', methods=['GET'])
def get_healthcheck():
    return flask.Response(status=200)
