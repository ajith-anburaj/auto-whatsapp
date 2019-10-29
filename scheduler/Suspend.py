from threading import Event


class Suspend(object):
    def __init__(self):
        self.event = Event()

    def sleep(self, seconds=None):
        self.event.clear()
        self.event.wait(timeout=seconds)

    def is_sleeping(self):
        return not self.event.is_set()

    def wake(self):
        self.event.set()
