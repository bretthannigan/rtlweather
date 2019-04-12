import threading
import subprocess
import time
import queue
import json
import rrdtool

class PollRTL433(threading.Thread):
    def __init__(self, out_q):
        super(PollRTL433, self).__init__()
        self.stdout = None
        self.stderr = None
        self.out_q = out_q
        self.stoprequest = threading.Event()

    def run(self):
        p = subprocess.Popen('rtl_433 -R 16 -F json -M time'.split(),
                             shell=False,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

        while not self.stoprequest.isSet():
            try:
                self.out_q.put((self.name, p.stdout.readline()))
            except queue.Empty:
                continue

    def join(self, timeout=None):
        self.stoprequest.set()
        super(PollRTL433, self).join(timeout)

out_q = queue.Queue()
rtl_433 = PollRTL433(out_q=out_q)
rtl_433.start()

while True:
    if not out_q.empty():
        print(out_q.get_nowait())