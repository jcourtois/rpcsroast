import multiprocessing

from rpcsroast.scale.fixtures import SimultaneousBurnIn, ScaleTestFixture
from cafe.drivers.unittest.decorators import tags


# note that we want test commands here that will return non-zero exit codes
# if anything fails.

KEYSTONE_SMOKE_TESTS_CMD = "echo hey7"
NEUTRON_SMOKE_TESTS_CMD = "echo 5325"
GLANCE_SMOKE_TESTS_CMD = "echo hey1"
NOVA_SMOKE_TESTS_CMD = "cafe-runner compute devstack -f -t \"type=smoke\""
HEAT_SMOKE_TESTS_CMD = "echo 6t53y7"
RABBIT_SMOKE_TESTS_CMD = "echo hey2"
GALERA_SMOKE_TESTS_CMD = "echo hey3"


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

        # while pinging rabbit and tracking success-to-failure ratio:

        #   find host
        #   write host file
        #   run rabbit playbook with new host file
        #   add new rabbitmq container ip to load balancer

        #   validate new rabbit server:
        #   -create message on message queue
        #   -submit
        #   -validate message sent
        #   -validate message queued
        #   -validate message consumed

    @tags(type='positive')
    def test_scale_infrastructure_down(self):
        # while pinging rabbit and tracking success-to-failure ratio:

        # select new rabbitmq container from cluster
        # run destroy-container playbook on that
        # remove ip from load balancer pool


