import logging
import logging.config

def configure_app_logger(loggername, log_path):
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '%(asctime)s : %(levelname)s : %(name)s : %(funcName)s : %(message)s'}
        },
        'handlers': {
            'file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'default',
                'filename': log_path,
                'maxBytes': 2000000,
                'backupCount': 3
            }
        },
        'loggers': {
            '__main__':{
                'level': 'INFO',
                'handlers': ['file']
            },
            'mongo.mongo_connect': {
                'level': 'INFO',
                'handlers': ['file']
            },
            'mykafka.kafka_connect': {
                'level': 'INFO',
                'handlers': ['file']
            }
        },
        'disable_existing_loggers': False
    })
    return logging.getLogger(loggername)


