import os
from datetime import timedelta, datetime
from mongoengine import connect
import mongoengine
from aiohttp import ClientHttpProxyError
from asyncio.exceptions import TimeoutError

from aiohttp.client_exceptions import (
    ClientProxyConnectionError,
    ServerDisconnectedError,
    ClientResponseError,
)

SECONDS_DELTA_BETWEEN_QUERIES = 120

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


def check_query_in_db(query: str, db_obj, date_end):
    """
    Function that performs search in "cache" DB whether there was such query or not
    :param query: string query that is a primary key in DB
    :param db_obj: DB object for search
    :param date_end: end date for filter comments
    :return: status, if there is such query
    """

    try:
        found = db_obj.objects(query=query).get()
    except mongoengine.DoesNotExist:
        found = None
    if not found:
        print("not found")
        return "Not found"
    elif date_end < found.timestamp:
        return "Already parsed"
    elif datetime.now() - found.timestamp > timedelta(seconds=SECONDS_DELTA_BETWEEN_QUERIES):
        print("found but time")
        return "Time"
    print("found")
    return "Found"


async def check_proxy(proxy_url, session, headers, proxy_auth):
    """
    Function that validates proxy
    :param proxy_url: URL of proxy server
    :param session: Open http session
    :param headers: headers of session and queries
    :param proxy_auth: Proxy credentials
    :return: Proxy URL if proxy is valid and None if not
    """
    print(proxy_url)
    print(proxy_auth)
    try:
        response = await session.get(
            url="http://localhost/healthcheck",
            headers=headers,
            proxy=proxy_url,
            proxy_auth=proxy_auth,
            timeout=5,
        )
        status = response.status
        print(status)
        if status == 200:
            return proxy_url
        else:
            return None
    except (
        ClientHttpProxyError,
        ConnectionRefusedError,
        TimeoutError,
        ClientProxyConnectionError,
        ServerDisconnectedError,
        ClientResponseError,
    ) as err:
        print(err)
        return None
