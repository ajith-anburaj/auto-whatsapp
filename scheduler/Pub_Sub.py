from uuid import uuid4


class Provider:
    def __init__(self):
        self.msg_queue = []
        self.subscribers = {}

    def notify(self, event, *args, **kwargs):
        self.msg_queue.append(event)
        if event in self.subscribers:
            for subscribers in self.subscribers[event]:
                for subscriber in self.subscribers[event][subscribers]:
                    subscriber(args, kwargs)

    def subscribe(self, sub_id, event, callback):
        self.subscribers.setdefault(event, {}).setdefault(sub_id, []).append(callback)

    def unsubscribe(self, sub_id, event):
        self.subscribers.get(event, {}).pop(sub_id, None)


class Publisher:
    def __init__(self, provider):
        self.provider = provider

    def publish(self, event, *args, **kwargs):
        self.provider.notify(event, args, kwargs=kwargs)


class Subscriber:
    def __init__(self, provider):
        self.id = str(uuid4())
        self.provider = provider

    def subscribe(self, event, callback):
        self.provider.subscribe(self.id, event, callback)

    def unsubscribe(self, event):
        self.provider.unsubscribe(self.id, event)
