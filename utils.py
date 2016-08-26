import logging
from pymongo import MongoClient

def make_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler("{}.log".format(logger_name))
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


def get_mongo_collection(collection_name):
    client = MongoClient('localhost', 27017)
    db = client['saltysports']
    collection = db[collection_name]

    return collection
