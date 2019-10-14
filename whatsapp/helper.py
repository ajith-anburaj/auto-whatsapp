import re


def is_valid_phone_number(number):
    return re.match('\+91[7-9][0-9]{9}', number)
