#!/usr/bin/env python3

# print date every 5 seconds for 10 times
import time
import datetime
import sys
import logging
import logging.handlers
import os 


def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    log_file = "/tmp/tprint.log"
    if os.path.exists(log_file):
        os.remove(log_file)
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = setup_logger("tprint")

n = 10
if len(sys.argv) > 1:
    n = int(sys.argv[1])

for i in range(n):
    print(i, datetime.datetime.now())
    logger.info(f'Iteration {i}, {datetime.datetime.now()}')
    sys.stdout.flush()
    time.sleep(1)
