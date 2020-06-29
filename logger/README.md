## Logging Module

Logging system provided by python as part of its standard library (logging) is used. Logging configuration used is of dictionary based configuration i.e. dictConfig().

### Usage 
```
from logger.applogger import *
LOG_FILE_NAME = "logs/generate_order.log"

if __name__ == "__main__":
    #Initialize logger to log all signals
    logger = configure_app_logger(__name__,LOG_FILE_NAME)
    logger.info("This is sample log file")
    main()

#Initialize logger to log all signals
logger = configure_app_logger(__name__,LOG_FILE_NAME)
```
### Sample log file
```
2020-06-28 03:49:52,602 : INFO : __main__ : main : This is sample log file
2020-06-28 03:49:52,611 : INFO : __main__ : publish_data_to_kafka : Kafka Producer Application Started ...
2020-06-28 03:49:52,734 : INFO : __main__ : publish_data_to_kafka : Raw orders published successfully.
2020-06-28 03:49:52,752 : INFO : __main__ : update_order_status : Orders Status changed to Generated successfully.

2020-06-28 07:17:30,409 : INFO : mongo.mongo_connect : my_mongo_db : Logger initialization done
```

### Implementation
* File Handlers are used for all the loggers and individual loggers are configured for each module.
* Default level setting for all loggers are configured as "INFO".
* File handler which is been used is of class "logging.handlers.RotatingFileHandler" to implement log file rotation.
* All the modules are been configured to write into their respective log_file.
* For file rotation max bytes is configured as 2000000 and copies preserved is 3.
* All the default values can be changed in applogger.py

