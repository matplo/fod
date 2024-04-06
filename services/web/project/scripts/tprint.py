#!/usr/bin/env python3

# print date every 5 seconds for 10 times
import time
import datetime
import sys

n = 10
if len(sys.argv) > 1:
    n = int(sys.argv[1])

for i in range(n):
    print(i, datetime.datetime.now())
    time.sleep(1)
