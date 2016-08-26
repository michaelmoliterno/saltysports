import logging
import requests
import requests_cache
import random
import time
from pymongo import MongoClient

# expire_after = 30 days
requests_cache.install_cache(expire_after=2592000)


def make_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler("saltysports.log".format(logger_name))
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

logger = make_logger("utils")


def get_mongo_collection(collection_name):
    client = MongoClient('localhost', 27017)
    db = client['saltysports']
    collection = db[collection_name]

    return collection

def get_response_from_target(target, attempt = 1, max_retries = 8):
    try:
        response = requests.get(target)
    except requests.exceptions.ConnectionError as e:
        logger.error("SKIPPING TARGET {} because {}".format(target,e.message))
        response = None

    if response.status_code == 200:
        # todo bueno
        pass
    elif response.status_code == 403:
        if attempt <= max_retries:
            logger.error("ATTEMPT {} FAILED SLEEPING ON TARGET {} because 403".format(attempt,target))
            sleepy_time(factor = attempt)
            attempt += 1
            get_response_from_target(target, attempt)
        else:
            logger.error("SKIPPING TARGET {} because 403".format(target))
            response = None
    else:
        logger.error("UNHANDLED status_code {} for {}".format(response.status_code,target))
        response = None

    return response

def sleepy_time(factor = 1, min_sleep = 2, max_sleep = 5, log = True):
    sleep_time = random.randint(min_sleep,max_sleep)
    sleep_time = sleep_time**factor
    if log:
        logger.info("SLEEPING FOR {} SECONDS".format(sleep_time))
    time.sleep(sleep_time)
