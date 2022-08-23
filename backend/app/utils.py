import os

import pymongo


def connect_mongo(db_name: str):
    """ Util to make a connection to the mongoDB
    :param db_name: Name of the certain database
    :return: Pointer to the certain DB
    """

    db_client = pymongo.MongoClient(
        "mongodb://mongoDB:27017/",
        username=os.environ.get('MONGO_ROOT_USER'),
        password=os.environ.get('MONGO_ROOT_PASSWORD'),
        serverSelectionTimeoutMS = 3000
    )
    try:
        print(db_client.server_info())
        return db_client[db_name]
    except Exception:
        print("Unable to connect to the server.")
        return None


