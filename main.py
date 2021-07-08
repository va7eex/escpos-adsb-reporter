import asyncio
from hexid import Hexid
import os
import redis
#import schedule
#import requests

from escpos.printer import Dummy, Network

_r = redis.Redis(host=os.getenv('REDIS_IP'), port=6379)

async def planelistener():
    hexid = Hexid()
    reader, writer = await asyncio.open_connection(
        os.getenv('PIAWARE_IP'), int(os.getenv('PIAWARE_PORT')))
    while True:
        data = await reader.readline()
        data = data.decode('utf-8').split(',')
        tailnum = hexid.lookup(data[4])
        if tailnum is not None:
            #TODO: make better
            #print(f'{data[4]}, {bindata}')
            report = _r.setnx(tailnum, 1)
            _r.expire(tailnum, 5)
            if report:
                print(f'New plane {tailnum}')

asyncio.run(planelistener())
