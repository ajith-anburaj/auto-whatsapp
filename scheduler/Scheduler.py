import json

from common.logger import logger
from scheduler.helper import process_schedule_time, time_difference_now, gen_key, convert_to_local_ts
from scheduler.Heap import Node, Heap
from scheduler.Pub_Sub import Publisher, Subscriber
from scheduler.Redis import Redis
from common.helper import idle


class Scheduler:
    def __init__(self, provider):
        self.redis = Redis()
        self.heap = self.construct_heap()
        self.provider = provider
        self.publisher = Publisher(self.provider)
        self.no_task = True

    def construct_heap(self):
        keys = self.redis.client.keys()
        nodes = []
        for key in keys:
            task_info = self.redis.client.get(key)
            task_info = process_schedule_time(json.loads(task_info))
            node = Node(key, task_info["timeInfo"]["schedule_time"])
            nodes.append(node)
        return Heap(nodes=nodes)

    def store_task_info(self, task_info):
        key = gen_key()
        task_info = process_schedule_time(task_info)
        task_info["id"] = key
        self.redis.client.set(key, json.dumps(task_info))
        self.heap.push(Node(key, task_info["timeInfo"]["schedule_time"]))

    def delete_task_by_id(self, task_id):
        return self.redis.client.delete(task_id)

    def get_next_task(self):
        task = self.heap.get_next_elements()[0]
        task = self.redis.client.get(task.id)
        return json.loads(task)

    def delete_task(self, task_info):
        logger.info(f'deleting task {task_info["id"]}')
        self.delete_task_by_id(task_info["id"])
        self.heap.pop()
        if task_info["recurring"] == "yes":
            self.store_task_info(task_info=task_info)

    def get_subscriber(self):
        return Subscriber(self.provider)

    def publish_event(self, event, task_info):
        self.publisher.publish(event)
        self.delete_task(task_info)

    def publish_task(self, task_info):
        logger.info(f'task publish {task_info["id"]}')
        self.publisher.publish("task", data=task_info)
        self.delete_task(task_info=task_info)

    def process_tasks(self):
        try:
            task = self.get_next_task()
            diff = time_difference_now(task["timeInfo"]["schedule_time"])
            next_task = convert_to_local_ts(task["timeInfo"]["schedule_time"], format_date=True)
            logger.debug(f'time difference for next task {diff}')
            if diff <= -1:
                self.delete_task(task_info=task)
            elif diff == 0:
                self.publish_task(task_info=task)
            elif diff > 15:
                logger.info(f'next task at {next_task}')
                idle(15 * 60)
            elif diff > 1:
                logger.debug(f'next task at {next_task}')
                idle(20)
            else:
                logger.debug(f'next task at {next_task} scheduler')
                idle(2)
        except IndexError:
            idle(20, 'scheduler')

    def start(self):
        while True:
            logger.debug("Processing")
            self.process_tasks()
