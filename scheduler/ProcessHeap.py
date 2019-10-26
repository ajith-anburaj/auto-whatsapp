import heapq
import json
from collections import namedtuple


class MyHeap(object):
    def __init__(self, initial=None, key=lambda x: x):
        self.key = key
        self.record = namedtuple('record', ['id', 'ts'])
        if initial:
            initial = json.loads(json.dumps(initial))
            self._data = [self.record(key(item['ts']), item['id']) for item in initial]
            heapq.heapify(self._data)
        else:
            self._data = []

    def push(self, item):
        item = json.loads(json.dumps(item))
        heapq.heappush(self._data, self.record(self.key(item['ts']), item['id']))
        print(list(self._data))

    def pop(self):
        return heapq.heappop(self._data)[1]

    def peek(self):
        return self._data[0]

    def get_heap(self):
        return list(self._data)
