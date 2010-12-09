import urllib
import json
import subprocess
from time import time, sleep

def g_index():
    u = urllib.urlopen("http://campdoc:campdoc@localhost:5984/ohloh_data/_design/ohloh2/_view/maxid")
    return json.load(u)['rows'][0]['value'] + 1

def run(id):
    proc = subprocess.Popen('python /mnt/hgfs/Projects/Data\ Getter/sources/ohloh.py %d' % id, stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=True)
    st = time()
    while (time() - st) < 60 and proc.poll() is None:
        if id != g_index():
            st = time()
            id = g_index()

        sleep(5)

    if proc.poll() is None:
        proc.kill()

id = g_index()
end = id + 1000
lcnt = 0
while id < end and lcnt < 100:
    run(id)
    id = g_index()

    lcnt += 1
    print lcnt, id
