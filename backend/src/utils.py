import os
from datetime import timedelta, datetime
from mongoengine import connect
from aiohttp import ClientHttpProxyError
from asyncio.exceptions import TimeoutError

from aiohttp.client_exceptions import (
    ClientProxyConnectionError,
    ServerDisconnectedError,
    ClientResponseError
)


def connect_mongo(db_name: str):
    """Util to make a connection to the mongoDB
    :param db_name: Name of the certain database
    :return: Pointer to the certain DB
    """
    db_client = connect(
        db=db_name,
        host="mongodb://mongoDB:27017/",
        username=os.environ.get("MONGO_ROOT_USER"),
        password=os.environ.get("MONGO_ROOT_PASSWORD"),
        serverSelectionTimeoutMS=3000,
        alias=db_name,
    )
    try:
        print(db_client.server_info())
        return db_client
    except Exception:
        print("Unable to connect to the server.")
        return None


def check_query_in_db(query: str, db_obj):
    # found = connection['QUERIES'].find(str.lower(query))
    found = db_obj.objects(query=query)
    if not found:
        print("not found")
        db_obj(query=query, timestamp=datetime.now()).save()
        return False
    elif datetime.now() - found[0].timestamp > timedelta(seconds=30):
        print("found but time")
        found.update(__raw__={"$set": {"timestamp": datetime.now()}})
        return False
    print("found")
    return True


async def check_proxy(proxy_url, session, headers):
    print(proxy_url)
    try:
        response = await session.get(
            url="http://wildberries.ru",
            headers=headers,
            proxy=proxy_url,
            timeout=2,
        )
        status = response.status
        print(status)
        if status == "200":
            return proxy_url
        else:
            return None
    except (
        ClientHttpProxyError,
        ConnectionRefusedError,
        TimeoutError,
        ClientProxyConnectionError,
        ServerDisconnectedError,
        ClientResponseError
    ) as err:
        print(err)
        return None
