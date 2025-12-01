import rpc
import logging
import time

from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)

cl = rpc.Client()
cl.run()

base_list = rpc.DBList({'foo'})
result_list = cl.runner(cl.append, lambda result: print("result: {}".format(result.value)), data='baz', db_list=base_list)

for i in range(15):
    time.sleep(1)
    print('working...')

cl.stop()
