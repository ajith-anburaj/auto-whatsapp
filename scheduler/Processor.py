import json
from uuid import uuid4
from time import sleep

import pendulum

from scheduler.Redis import Redis
from scheduler.Heap import Node, Heap
from scheduler.helper import process_schedule_time, time_difference_now
from scheduler.Pub_Sub import Provider, Publisher, Subscriber


class Processor:

    def __init__(self):
        self.redis = Redis()
        self.heap = self.construct_heap()
        self.provider = Provider()
        self.publisher = Publisher(self.provider)
        self.no_task = True

    def construct_heap(self):
        keys = self.redis.client.keys()
        nodes = []
        for key in keys:
            task_info = self.redis.client.get(key)
            task_info = process_schedule_time(json.loads(task_info))
            node = Node(key, task_info['timeInfo']['schedule_time'])
            nodes.append(node)
        return Heap(nodes=nodes)

    def store_task_info(self, task_info):
        key = str(uuid4())
        task_info = process_schedule_time(task_info)
        task_info['id'] = key
        self.redis.client.set(key, json.dumps(task_info))
        self.heap.push(Node(key, task_info['timeInfo']['schedule_time']))

    def delete_task_by_id(self, task_id):
        return self.redis.client.delete(task_id)

    def get_next_task(self):
        task = self.heap.get_next_elements()[0]
        task = self.redis.client.get(task.id)
        return json.loads(task)

    def _post_process(self, task_info):
        self.delete_task_by_id(task_info['id'])
        self.heap.pop()
        print(f'deleting task {task_info["id"]}')
        if task_info['recurring'] == 'yes':
            self.store_task_info(task_info=task_info)

    def get_subscriber(self):
        return Subscriber(self.provider)

    def publish_event(self, event, task_info):
        self.publisher.publish(event)
        self._post_process(task_info)

    def start(self):
        while True:
            print('Processing')
            try:
                task = self.get_next_task()
                diff = time_difference_now(task['timeInfo']['schedule_time'])
                print(diff)
                if diff <= -1:
                    self._post_process(task_info=task)
                    print(f'task diff {diff} task {task["id"]}')
                elif diff == 0:
                    print(f'task publish {task["id"]}')
                    self.publisher.publish('task', data=task)
                    self._post_process(task_info=task)
                elif diff > 15:
                    print('sleeping for 15 minutes')
                    sleep(15 * 60)
                else:
                    print(
                        f'current time {pendulum.now().to_datetime_string()} next task at {pendulum.from_timestamp(task["timeInfo"]["schedule_time"]).to_datetime_string()}')
                    print('sleeping for 30')
                    sleep(20)
            except IndexError:
                print('Sleeping')
                sleep(20)
