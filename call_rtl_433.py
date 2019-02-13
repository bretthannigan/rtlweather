import threading
import subprocess
import time
import queue
import json

class PollRTL433(threading.Thread):
    def __init__(self, out_q):
        super(PollRTL433, self).__init__()
        self.stdout = None
        self.stderr = None
        #threading.Thread.__init__(self)
        self.out_q = out_q
        self.stoprequest = threading.Event()

    def run(self):
        p = subprocess.Popen('ping -t google.com'.split(),
                             shell=False,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

        #self.stdout, self.stderr = p.communicate()

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

time.sleep(0.1)
print("1:")
print(out_q.get_nowait())
time.sleep(0.1)
print("2:")
print(out_q.get_nowait())
time.sleep(0.1)
print("3:")
print(out_q.get_nowait())
time.sleep(0.1)
print("4:")
print(out_q.get_nowait())
time.sleep(0.1)
print("5:")
print(out_q.get_nowait())
rtl_433.join()