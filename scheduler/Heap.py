import datetime
import heapq
from dataclasses import dataclass


@dataclass
class Node:
    id: str
    ts: int

    def __lt__(self, other):
        return datetime.datetime.fromtimestamp(self.ts) < datetime.datetime.fromtimestamp(other.ts)


class Heap:
    def __init__(self, nodes):
        self.heap = nodes
        heapq.heapify(nodes)

    def push(self, node):
        heapq.heappush(self.heap, node)

    def pop(self):
        heapq.heappop(self.heap)

    def get_next_elements(self, count=1):
        return heapq.nsmallest(count, self.heap)
