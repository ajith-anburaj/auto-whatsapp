from scheduler.ProcessHeap import MyHeap


class Schedule:

    def __init__(self, data=None):
        if data:
            self.Heap = MyHeap(data)
        else:
            self.Heap = MyHeap()

    def schedule_task(self, node_details):
        MyHeap.push(self.Heap, node_details)
        print('task scheduled')

    def process_task(self):
        print(self.Heap.peek())
        # to do
        # while next task is in 15 min, take it and publish
