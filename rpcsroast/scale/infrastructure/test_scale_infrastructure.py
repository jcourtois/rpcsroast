import multiprocessing

from rpcsroast.scale.fixtures import SimultaneousBurnIn, ScaleTestFixture
from cafe.drivers.unittest.decorators import tags


# note that we want test commands here that will return non-zero exit codes
# if anything fails.

KEYSTONE_SMOKE_TESTS_CMD = "curl http://localhost:5000/v2.0"
NEUTRON_SMOKE_TESTS_CMD = "echo hey neutron"
GLANCE_SMOKE_TESTS_CMD = "echo hey glance"
NOVA_SMOKE_TESTS_CMD = "curl http://localhost:8774/v2.0"
HEAT_SMOKE_TESTS_CMD = "echo hey heat"
RABBIT_SMOKE_TESTS_CMD = "echo hey rabbit"
GALERA_SMOKE_TESTS_CMD = "echo hey galera"


class ScaleInfrastructureTest(ScaleTestFixture):

    @classmethod
    def setUpClass(cls):
        super(ScaleInfrastructureTest, cls).setUpClass()
        cls.sentinel = multiprocessing.Event()
        cls.burn_ins = [
            SimultaneousBurnIn(KEYSTONE_SMOKE_TESTS_CMD, cls.sentinel),
            SimultaneousBurnIn(NEUTRON_SMOKE_TESTS_CMD, cls.sentinel),
            SimultaneousBurnIn(GLANCE_SMOKE_TESTS_CMD, cls.sentinel),
            SimultaneousBurnIn(NOVA_SMOKE_TESTS_CMD, cls.sentinel),
            SimultaneousBurnIn(HEAT_SMOKE_TESTS_CMD, cls.sentinel),
            SimultaneousBurnIn(RABBIT_SMOKE_TESTS_CMD, cls.sentinel),
            SimultaneousBurnIn(GALERA_SMOKE_TESTS_CMD, cls.sentinel)]

    @tags(type='positive')
    def test_scale_infrastructure_up(self):
        for burn_in in self.burn_ins:
            burn_in.start()

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


    @tags(type='positive')
    def test_scale_infrastructure_down(self):
        pass
        # while pinging rabbit and tracking success-to-failure ratio:

        # select new rabbitmq container from cluster
        # run destroy-container playbook on that
        # remove ip from load balancer pool


