import os
from json import loads
from multiprocessing import Process
from multiprocessing.managers import BaseManager
from time import sleep

import pendulum

from config import config
from common.logger import logger
from scheduler.helper import convert_to_local_ts
from scheduler.Pub_Sub import Provider
from scheduler.Scheduler import Scheduler
from whatsapp.WhatsApp import WhatsApp
from common.helper import idle
from common.load_env import load_env

load_env()

driver_config = {
    "binary_location": config.binary_location,
    "fire_fox_driver_path": config.fire_fox_driver_path,
    "driver_headless": config.driver_headless,
    "fire_fox_profile_path": config.fire_fox_profile_path,
}

client: WhatsApp
provider_instance = None
scheduler_instance: Scheduler


class CustomManager(BaseManager):
    pass


def send_message(_, kwargs):
    global client
    logger.debug(f'Scheduler started at PID:{os.getpid()}')
    data = kwargs["data"]
    client.send_message(data["contact"], data["message"], data["type"])
    scheduled_time = convert_to_local_ts(data["timeInfo"]["schedule_time"], format_date=True)
    current_time = pendulum.now().to_datetime_string()
    logger.info(f'scheduled at {scheduled_time} sent at {current_time}')


def scheduler_suspend(_, kwargs):
    client.close_whats_app()
    logger.info(f'Scheduler sleeping for {kwargs["data"] // 60} minutes')


def scheduler_wake_up(_, kwargs):
    launch_whats_app()
    logger.info('Scheduler wake up')


def subscribe_events(sub):
    sub.subscribe("task", send_message)
    sub.subscribe("sleep", scheduler_suspend)
    sub.subscribe("wake", scheduler_wake_up)


def start_scheduler(scheduler):
    sub = scheduler.get_subscriber()
    subscribe_events(sub)
    while True:
        if pendulum.now().second == 0 or pendulum.now() == 1:
            break
        sleep(1)
    scheduler.start()


def request_for_task(scheduler):
    while True:
        task = input("Enter the task details: ")
        scheduler.store_task_info(task_info=loads(task))
        logger.info(f'Task stored {task}')


def bind_shared_objects(manager):
    global provider_instance, scheduler_instance
    provider_instance = manager.Provider()
    scheduler_instance = manager.Scheduler(provider_instance)
    return [provider_instance, scheduler_instance]


def launch_whats_app():
    global client
    logger.info("Auto whats app started!!!")
    client = WhatsApp(driver_config)
    client.open_whats_app_web()
    idle(1, 'main opened whats app')


def start():
    launch_whats_app()
    CustomManager.register('Scheduler', Scheduler)
    CustomManager.register('Provider', Provider)
    manager = CustomManager()
    manager.start()
    global provider_instance, scheduler_instance
    # noinspection PyTypeChecker
    provider_instance, scheduler_instance = bind_shared_objects(manager)
    scheduler_process = Process(target=start_scheduler, args=[scheduler_instance], daemon=True)
    scheduler_process.start()


if __name__ == "__main__":
    start()
