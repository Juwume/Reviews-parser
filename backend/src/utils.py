import os
from datetime import timedelta, datetime
from mongoengine import connect


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
