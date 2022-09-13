import flask
from app import app
from .scripts import download_wildberries_comments
from .utils import connect_mongo, check_query_in_db
from .models.WB import ProductWB, QueryWB
from flask import request


@app.route('/')
def index():
    return {'message': 'Hello, this is my diploma work'}


@app.route('/api/wb/<string:query>', methods=['GET'])
async def parse_wb(query):
    connector = connect_mongo('WILDBERRIES')
    is_in_db = check_query_in_db(query, QueryWB)
    products = []
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


@app.route('/parser/api/v1.0/yamarket/<string:query>', methods=['GET'])
def parse_yamarket(query):
    pass


@app.route('/parser/api/v1.0/petshop/<string:query>', methods=['GET'])
def parse_petshop(query):
    pass
