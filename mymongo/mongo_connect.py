from logger.applogger import *
from pymongo.errors import ConnectionFailure
from pymongo import MongoClient

class my_mongo_db(object):
    _log = '/home/mazin/stage2/logs/mongo_connect.log'
    _host ="10.0.0.7"
    _port = 27017
    _db_name = "locations"
    logger = configure_app_logger(__name__,_log)
    logger.info("Logger initialization done")
    try:
        _client = MongoClient(_host,_port)
        db = _client[_db_name]
    except ConnectionFailure as conn_err:
        logger.error(f"Exception while Updating the status in mongo:{conn_err.strerror}")
        sys.exit(1)
    except Exception as ex_err:
        logger.error(f"Exception while Updating the status in mongo:{ex_err.strerror}")
        sys.exit(1)

