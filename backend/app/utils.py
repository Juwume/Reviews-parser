import os
from datetime import timedelta, datetime
import motor.motor_asyncio


async def connect_mongo(db_name: str):
    """ Util to make a connection to the mongoDB
    :param db_name: Name of the certain database
    :return: Pointer to the certain DB
    """

    db_client = motor.motor_asyncio.AsyncIOMotorClient(
        "mongodb://mongoDB:27017/",
        username=os.environ.get('MONGO_ROOT_USER'),
        password=os.environ.get('MONGO_ROOT_PASSWORD'),
        serverSelectionTimeoutMS = 3000
    )
    try:
        print(await db_client.server_info())
        return db_client[db_name]
    except Exception:
        print("Unable to connect to the server.")
        return None


async def check_query_in_db(query: str, connection):
    found = await connection['QUERIES'].find_one(str.lower(query))
    if not found or (datetime.now() - datetime.strptime(found.get('last_ask_timestamp'),'%Y-%m-%d-%h:%m:%s') > timedelta(hours=1)):
        return False
    else:
        return True


