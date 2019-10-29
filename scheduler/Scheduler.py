import os
import json

from common.logger import logger
from scheduler.helper import *
from scheduler.Heap import Node, Heap
from scheduler.Pub_Sub import Publisher, Subscriber
from scheduler.Redis import Redis
from common.helper import idle
from scheduler.Suspend import Suspend


class Scheduler:
    user_pattern = f'{os.environ["USER"]}:'

    def __init__(self, provider):
        self.redis = Redis()
        self.heap = self.construct_heap()
        self.provider = provider
        self.publisher = Publisher(self.provider)
        self.no_task = True
        self.suspend = Suspend()

    def get_user_tasks(self):
        pattern = f'{Scheduler.user_pattern}*'
        keys = self.redis.client.keys(pattern=pattern)
        tasks = []
        for key in keys:
            task_info = self.redis.client.get(key)
            task_info = process_schedule_time(json.loads(task_info))
            tasks.append(task_info)
        return tasks

    def construct_heap(self):
        nodes = []
        tasks = self.get_user_tasks()
        for task_info in tasks:
            node = Node(task_info['id'], task_info["timeInfo"]["schedule_time"])
            nodes.append(node)
        return Heap(nodes=nodes)

    def store_task_info(self, task_info):
        key = gen_key() if "id" not in task_info else task_info["id"]
        task_info["id"] = key
        task_info = process_schedule_time(task_info)
        self.redis.client.set(key, json.dumps(task_info))
        self.heap.push(Node(key, task_info["timeInfo"]["schedule_time"]))
        self.wake_up()
        return task_info

    def delete_all_tasks(self):
        pattern = f'{Scheduler.user_pattern}*'
        keys = self.redis.client.keys(pattern=pattern)
        self.redis.client.delete(*keys)
        self.heap = []

    def get_task_by_id(self, task_id):
        return self.redis.client.get(name=task_id)

    def update_task_by_id(self, task_id, task_update_info):
        task = self.get_task_by_id(task_id=task_id)
        if task is not None:
            task = json.loads(task)
            updated_task_info = merge_dictionaries(task, task_update_info)
            if updated_task_info["recurring"] == "yes":
                updated_task_info["timeInfo"].pop("schedule_time")
            updated_task_info = process_schedule_time(task_info=updated_task_info)
            self.delete_task_by_id(task_id=task_id, top_element=False)
            self.redis.client.set(updated_task_info['id'], json.dumps(updated_task_info))
            self.heap.push(Node(id=task_id, ts=updated_task_info))
            self.wake_up()
            return updated_task_info
        else:
            return False

    def delete_task_by_id(self, task_id, top_element=True):
        logger.info(f'deleting task {task_id}')
        self.redis.client.delete(task_id)
        return self.heap.pop() if top_element else self.heap.pop_by_id(task_id)

    def get_next_task(self):
        task = self.heap.get_next_elements()[0]
        task = self.redis.client.get(task.id)
        return json.loads(task)

    def get_subscriber(self):
        return Subscriber(self.provider)

    def publish_task(self, task_info):
        logger.info(f'task publish {task_info["id"]}')
        self.publisher.publish("task", data=task_info)
        self.delete_task_by_id(task_id=task_info['id'])
        self.handle_recurring(task_info=task_info)

    def handle_recurring(self, task_info):
        if task_info["recurring"] == "yes":
            self.store_task_info(task_info=task_info)

    def wake_up(self):
        if self.suspend.is_sleeping():
            self.suspend.wake()
            self.publisher.publish('wake')

    def sleep(self, diff):
        sleep_interval = 60 * 15 if diff < 30 else diff - (60 * 15)
        self.publisher.publish('sleep', data=sleep_interval)
        self.suspend.sleep(sleep_interval)

    def process_tasks(self):
        try:
            task = self.get_next_task()
            diff = time_difference_now(task["timeInfo"]["schedule_time"])
            next_task = convert_to_local_ts(task["timeInfo"]["schedule_time"], format_date=True)
            logger.debug(f'time difference for next task {diff}')
            if diff <= -1:
                self.delete_task_by_id(task_id=task['id'])
                self.handle_recurring(task_info=task)
            elif diff == 0:
                self.publish_task(task_info=task)
            elif diff > 15:
                logger.info(f'next task at {next_task}')
                self.sleep(diff)
            elif diff > 1:
                logger.debug(f'next task at {next_task}')
                idle(20)
            else:
                logger.debug(f'next task at {next_task} scheduler')
                idle(2)
        except IndexError:
            self.sleep(60 * 60 * 24)

    def start(self):
        while True:
            logger.debug("Processing")
            self.process_tasks()
