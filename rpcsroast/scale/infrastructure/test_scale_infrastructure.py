import multiprocessing
import time

from rpcsroast.scale.fixtures import SimultaneousBurnIn, ScaleTestFixture
from cafe.drivers.unittest.decorators import tags


# note that we want test commands here that will return non-zero exit codes
# if anything fails.
from rpcsroast.scale.infrastructure.rabbit.rabbit_health_check import \
    RabbitSimultaneousBurnIn

#use ab instead of curl; it's for load testing
curl_command = "curl -f {} -s >/dev/null"

smoke_test = {
    "keystone-api": curl_command.format("http://localhost:5000/"),
    "glance-api": curl_command.format("http://localhost:9292/"),
    "cinder-api": curl_command.format("http://localhost:8776/"),
    "nova-api": curl_command.format("http://localhost:8774/"),
    "heat-api": curl_command.format("http://localhost:8004/"),
    "heat-api-cloudwatch": curl_command.format("http://localhost:8003/"),
    "heat-api-cfn": curl_command.format("http://localhost:8000/"),
    "database": "mysqlslap --delimiter=\";\" "
    "--create=\"CREATE TABLE a (b int);INSERT INTO a VALUES (23)\" "
    "--query=\"SELECT * FROM a\" --concurrency=50 --iterations=20 "
    "--password=\"stack\" --detach=1 >/dev/null"
}


class ScaleInfrastructureTest(ScaleTestFixture):

    @classmethod
    def setUpClass(cls):
        super(ScaleInfrastructureTest, cls).setUpClass()
        cls.sentinel = multiprocessing.Event()
        cls.api_successes = multiprocessing.Value('i', 0)
        cls.api_failures = multiprocessing.Value('i', 0)
        cls.burn_ins = [
            SimultaneousBurnIn(smoke_test['keystone-api'],
                               cls.api_successes,
                               cls.api_failures,
                               cls.sentinel),
            SimultaneousBurnIn(smoke_test['glance-api'],
                               cls.api_successes,
                               cls.api_failures,
                               cls.sentinel),
            SimultaneousBurnIn(smoke_test['cinder-api'],
                               cls.api_successes,
                               cls.api_failures,
                               cls.sentinel),
            SimultaneousBurnIn(smoke_test['nova-api'],
                               cls.api_successes,
                               cls.api_failures,
                               cls.sentinel),
            SimultaneousBurnIn(smoke_test['heat-api'],
                               cls.api_successes,
                               cls.api_failures,
                               cls.sentinel),
            SimultaneousBurnIn(smoke_test['heat-api-cloudwatch'],
                               cls.api_successes,
                               cls.api_failures,
                               cls.sentinel),
            SimultaneousBurnIn(smoke_test['heat-api-cfn'],
                               cls.api_successes,
                               cls.api_failures,
                               cls.sentinel),
            SimultaneousBurnIn(smoke_test['database'],
                               cls.api_successes,
                               cls.api_failures,
                               cls.sentinel),
            RabbitSimultaneousBurnIn(cls.api_successes,
                                     cls.api_failures,
                                     cls.sentinel)]

    @tags(type='positive')
    def test_scale_infrastructure_up(self):
        for burn_in in self.burn_ins:
            burn_in.start()
        time.sleep(3)
        #   find host
        #   write host file
        #   run rabbit playbook with new host file
        #   add new rabbitmq container ip to load balancer

        # ask load balancer about service on IP
        #   validate new rabbit server:
        #   -create message on message queue
        #   -submit
        #   -validate message sent
        #   -validate message queued
        #   -validate message consumed
        self.sentinel.set()
        for burn_in in self.burn_ins:
            burn_in.join()
        print "\nSuccesses: {}\nFailures: {}".format(self.api_successes.value,
                                                     self.api_failures.value)


    @tags(type='positive')
    def test_scale_infrastructure_down(self):
        pass
        # while pinging rabbit and tracking success-to-failure ratio:

        # select new rabbitmq container from cluster
        # run destroy-container playbook on that
        # remove ip from load balancer pool
