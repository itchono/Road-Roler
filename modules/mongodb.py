'''
MongoDB Database for Comrade
'''
import sys
import os
import pymongo
from pymongo.collection import Collection

mongo_client = None
db = None


def setup():
    '''
    Runs during startup to set up the databases
    The rationale is to defer execution until .env is loaded
    '''
    global mongo_client, db
    try:
        mongo_client = pymongo.MongoClient(os.environ.get("MONGOKEY"))
    except Exception:
        print("MongoDB Could not be connected. Check that you have "
                        "the correct MongoDB key in your .env file, and "
                        "the that you have dnspython installed"
                        "\nTerminating program...")
        sys.exit(1)  # Exit with error

    db = mongo_client[mongo_client.list_database_names()[0]]
    print("MongoDB Atlas connected to: "
                f"{mongo_client.list_database_names()[0]}")


# Convenience method to return collection by name in configuration
def collection(name) -> Collection:
    try:
        return db[name]
    except Exception:
        return None
