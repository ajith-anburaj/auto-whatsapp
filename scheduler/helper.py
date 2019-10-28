import os
from uuid import uuid4

import pendulum

from common.helper import convert_to_local_ts


def gen_key():
    return f'{os.environ["USER"]}:{str(uuid4())}'


def reset_seconds(time):
    return time.set(second=0).int_timestamp


def process_schedule_time(task_info):
    time_info = task_info["timeInfo"]
    if "ts" in time_info:
        time_info["schedule_time"] = reset_seconds(convert_to_local_ts(time_info["ts"]))
    else:
        time_units = {"day": 1440, "hour": 60, "minute": 1}
        time_in_minutes = time_units[time_info["unit"]] * time_info["value"]
        time_info["schedule_time"] = (reset_seconds(pendulum.now().add(minutes=time_in_minutes)))
        task_info["timeInfo"] = time_info
    return task_info


def merge_dictionaries(original, update):
    for key, value in update.items():
        if isinstance(value, dict):
            merge_dictionaries(original[key], value)
        else:
            original[key] = value
    return original


def time_difference_now(ts):
    task_time = convert_to_local_ts(ts)
    current = pendulum.now().set(second=0)
    diff = current.diff(task_time, False).in_minutes()
    return (
        0
        if current.to_datetime_string() == task_time.to_datetime_string()
        else 1
        if (diff == 0 or diff == -1)
        else -1
        if diff < -1
        else diff
    )
