from time import sleep

import pendulum

from whatsapp.WhatsApp import WhatsApp
import whatsapp.Constants as Constants
from scheduler.Processor import Processor
import config

driver_config = {
    'binary_location': config.binary_location,
    'fire_fox_driver_path': config.fire_fox_driver_path,
    'driver_headless': config.driver_headless,
    'fire_fox_profile_path': config.fire_fox_profile_path
}


def send_message(args, kwargs):
    data = kwargs['kwargs']['data']
    client.send_message(data['contact'], data['message'], data['type'])
    print(
        f'scheduled {pendulum.from_timestamp(data["timeInfo"]["schedule_time"]).to_datetime_string()} sent {pendulum.now().to_datetime_string()}')


if __name__ == '__main__':
    client = WhatsApp(driver_config)
    client.open_whats_app_web()
    sleep(10)
    scheduler = Processor()
    task_details = {
        'contact': 'ME',
        'message': 'Testing please ignore',
        'type': Constants.TEXT,
        'recurring': 'no',
        'timeInfo': {
            'unit': 'minute',
            'value': 4
        }
    }
    task_details1 = {
        'contact': 'ME',
        'message': 'Testing please ignore!!!!',
        'type': 'text',
        'recurring': 'yes',
        'timeInfo': {
            'unit': 'minute',
            'value': 2
        }
    }
    scheduler.store_task_info(task_info=task_details)
    scheduler.store_task_info(task_info=task_details1)
    sub = scheduler.get_subscriber()
    sub.subscribe('task', send_message)
    while True:
        if pendulum.now().second == 0 or pendulum.now() == 1:
            break
        sleep(1)
    scheduler.start()
