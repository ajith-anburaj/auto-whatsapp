import pendulum


def process_schedule_time(task_info):
    time_info = task_info['timeInfo']
    if 'ts' in time_info:
        time_info['schedule_time'] = time_info['ts']
    else:
        time_units = {
            'day': 1440,
            'hour': 60,
            'minute': 1,
        }
        time_in_minutes = time_units[time_info['unit']] * time_info['value']
        time_info['schedule_time'] = pendulum.now().add(minutes=time_in_minutes).int_timestamp
        task_info['timeInfo'] = time_info
    return task_info


def time_difference_now(ts):
    timestamp = pendulum.from_timestamp(ts)
    diff = pendulum.now().diff(timestamp, False).in_minutes()
    return 0 if diff == -1 else -1 if diff < -1 else diff
