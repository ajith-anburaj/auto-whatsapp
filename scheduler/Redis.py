import redis


class Redis:

    def __init__(self):
        self.client = redis.Redis(
            host='redis-19718.c13.us-east-1-3.ec2.cloud.redislabs.com',
            port='19718',
            password='WlTZ3bMDFPHixrADIRZXn9zyIlqIVMdM')
