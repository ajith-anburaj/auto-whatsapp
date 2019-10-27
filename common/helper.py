from time import sleep
import re

import pendulum

from common.logger import logger


def idle(secs, process=''):
    time = f'{secs // 60} minutes' if secs > 60 else f'{secs} seconds'
    logger.debug(f'{process}: Sleeping for {time}')
    sleep(secs)


def convert_to_local_ts(ts, format_date=False):
    # noinspection PyTypeChecker
    timestamp = pendulum.from_timestamp(ts, "Asia/Kolkata")
    return timestamp.to_datetime_string() if format_date else timestamp


def is_valid_phone_number(number):
    return re.match("'+'91[7-9][0-9]{9}", number)
