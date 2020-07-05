from logger.applogger import *
from pymongo.errors import ConnectionFailure
from pymongo import MongoClient

class MyMongoDb(object):
    log = '/home/mazin/stage2/logs/mongo_connect.log'
    host ="10.0.0.7"
    port = 27017
    db_name = "locations"
    logger = configure_app_logger(__name__,log)
    logger.info("Logger initialization done")
    try:
        _client = MongoClient(host,port)
        db = _client[db_name]
    except ConnectionFailure as conn_err:
        logger.error(f"Exception while Updating the status in mongo:{conn_err}")
        sys.exit(1)
    except Exception as ex_err:
        logger.error(f"Exception while Updating the status in mongo:{ex_err}")
        sys.exit(1)

