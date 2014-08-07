import random
import kombu
import time
from rpcsroast.scale.fixtures import SimultaneousBurnIn


class RabbitSimultaneousBurnIn(SimultaneousBurnIn):
    def __init__(self, successes, failures, sentinel_event):
        super(RabbitSimultaneousBurnIn,
              self).__init__('', successes, failures, sentinel_event)

    def run(self):
        connection = kombu.Connection(hostname='localhost', password='stack')
        while not self.sentinel_event.is_set():
            messages = [str(random.uniform(0, 1)),
                        str(random.uniform(0, 1)),
                        str(random.uniform(0, 1))]
            received_messages = set()

            with connection.SimpleBuffer('test_queue3') as queue:
                for message in messages:
                    queue.put(message)
                    time.sleep(0.1)  # to give rabbit a break

                for _ in range(queue.qsize()):
                    received_messages.add(queue.get(timeout=1).body)

            for message in messages:
                if message in received_messages:
                    with self.successes.get_lock():
                        self.successes.value += 1
                else:
                    with self.failures.get_lock():
                        self.failures.value += 1
