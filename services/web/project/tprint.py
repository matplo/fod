#!/usr/bin/env python3

# print date every 5 seconds for 10 times
import time
import datetime


for i in range(10):
    print(datetime.datetime.now())
    time.sleep(5)
