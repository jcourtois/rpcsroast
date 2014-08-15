import time
import yaml
import ansible.playbook
import multiprocessing


from rpcsroast.scale.fixtures import SimultaneousBurnIn, ScaleTestFixture
from cafe.drivers.unittest.decorators import tags


from rpcsroast.scale.infrastructure.rabbit.rabbit_health_check import \
    RabbitSimultaneousBurnIn

curl_command = "curl -f {} -s >/dev/null"

smoke_test = {
    "keystone-api": curl_command.format("http://localhost:5000/"),
    "glance-api": curl_command.format("http://localhost:9292/"),
    "cinder-api": curl_command.format("http://localhost:8776/"),
    "nova-api": curl_command.format("http://localhost:8774/"),
    "heat-api": curl_command.format("http://localhost:8004/"),
    "heat-api-cloudwatch": curl_command.format("http://localhost:8003/"),
    "heat-api-cfn": curl_command.format("http://localhost:8000/"),
    "neutron-api": curl_command.format("http://localhost:9696/"),
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
            SimultaneousBurnIn(smoke_test['neutron-api'],
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
    def test_scale_infrastructure_up_and_down(self):
        for burn_in in self.burn_ins:
            burn_in.start()

        with open('rpc_user_config.yml', 'r') as stream:
            contents = yaml.load(stream.read())

        contents['infra_hosts']['scale1'] = {'ip': '10.0.0.10'}
        contents['infra_hosts']['scale2'] = {'ip': '10.0.0.11'}

        with open('upscale_infra_config.yml', 'w') as stream:
            stream.write(yaml.dump(contents))

        scale_up_playbook = ansible.playbook.PlayBook(
            playbook="playbooks/infrastructure/"
                     "all-the-infrastructure-things.yml",
            extra_vars="@upscale_infra_config.yml")
        scale_up_playbook.run()

        # validate load balancer sees new hosts
        # validate new hosts

        scale_down_playbook = ansible.playbook.PlayBook(
            playbook="playbooks/infrastructure/"
                     "all-the-infrastructure-things.yml",
            extra_vars="@rpc_user_config.yml")
        scale_down_playbook.run()
        # remove created config file
        # (delete new entry from inventory??)
        self.sentinel.set()
        for burn_in in self.burn_ins:
            burn_in.join()
        print "\nSuccesses: {}\nFailures: {}".format(self.api_successes.value,
                                                     self.api_failures.value)
