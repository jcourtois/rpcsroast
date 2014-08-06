import kombu
import time
from random import uniform
from rpcsroast.scale.fixtures import SimultaneousBurnIn


class RabbitSimultaneousBurnIn(SimultaneousBurnIn):
    def __init__(self, successes, failures, sentinel_event):
        super(RabbitSimultaneousBurnIn,
              self).__init__('', successes, failures, sentinel_event)

    def run(self):
        connection = kombu.Connection(hostname='localhost', password='stack')
        queue = connection.SimpleQueue('test_queue')
        while not self.sentinel_event.is_set():
            time.sleep(0.1)
            messages = [uniform(0, 1), uniform(0, 1), uniform(0, 1)]
            received_messages = set()

            for message in messages:
                queue.put(message)

            for _ in range(queue.qsize()):
                received_messages.add(queue.get(timeout=1))

            if all(message in received_messages for message in messages):
                with self.successes.get_lock():
                    self.successes.value += 1
                    print "Rabbit success!!"
            else:
                with self.failures.get_lock():
                    self.failures.value += 1
                print "Rabbit failure!!" \
                      ""
