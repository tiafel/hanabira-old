# Some useful context managers

class locked(object):
    def __init__(self, lock):
        self.lock = lock
    def __enter__(self):
        self.lock.acquire()
    def __exit__(self, *exc_info):
        self.lock.release()
