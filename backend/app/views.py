import flask
from app import app
from .scripts import download_wildberries_products, download_wildberries_comments,download_wildberries_imt_id
from .utils import connect_mongo
from flask import request


@app.route('/')
def index():
    return {'message': 'Hello, this is my diploma work'}


@app.route('/parser/api/v1.0/wb/<string:query>', methods=['GET'])
async def parse_wb(query):
    connector = connect_mongo('wildberries')
    await download_wildberries_products([query], connector)
    return flask.Response(status=200)
    # download_wildberries_products()


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
