from cafe.drivers.unittest.fixtures import BaseTestFixture
import multiprocessing
import subprocess
import time


class ScaleTestFixture(BaseTestFixture):
    pass


class SimultaneousBurnIn(multiprocessing.Process):

    def __init__(self, burn_in_command, sentinel_event):
        """
        :param burn_in_command: (ideally this test-runner command will run a
        non-zero exit code if any tests fail.  Thus, it may be recommendable
        to set the testing to fail fast.
        :type burn_in_command: str
        :param sentinel_event: an event that signals that the burn-in tests can
        stop running.
        :type sentinel_event: multiprocessing.Event
        """
        multiprocessing.Process.__init__(self)
        self.burn_in_command = burn_in_command
        self.sentinel_event = sentinel_event
        self.success_counter = 0
        self.failure_counter = 0

    @property
    def total_tests_ran(self):
        return self.success_counter + self.failure_counter

    def run(self):
        while not self.sentinel_event.is_set():
            time.sleep(0.1)
            test_run = subprocess.Popen(self.burn_in_command, shell=True)
            if test_run.returncode == 0:
                self.success_counter += 1
            else:
                self.failure_counter += 1
