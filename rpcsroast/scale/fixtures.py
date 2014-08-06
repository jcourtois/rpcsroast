from cafe.drivers.unittest.fixtures import BaseTestFixture
import multiprocessing
import subprocess
import time


class ScaleTestFixture(BaseTestFixture):
    pass


class SimultaneousBurnIn(multiprocessing.Process):
    def __init__(self, burn_in_command, successes, failures, sentinel_event):
        """
        :param burn_in_command: (ideally this test-runner command will run a
        non-zero exit code if any tests fail.  Thus, it may be recommendable
        to set the testing to fail fast.
        :type burn_in_command: str
        :type successes: multiprocessing.Value
        :type failures: multiprocessing.Value
        :param sentinel_event: an event that signals that the burn-in tests can
        stop running.
        :type sentinel_event: multiprocessing.Event
        """
        multiprocessing.Process.__init__(self)
        self.burn_in_command = burn_in_command
        self.successes = successes
        self.failures = failures
        self.sentinel_event = sentinel_event

    def run(self):
        while not self.sentinel_event.is_set():
            time.sleep(0.1)
            test_run = subprocess.Popen(self.burn_in_command, shell=True)
            test_run.wait()
            if test_run.returncode == 0:
                with self.successes.get_lock():
                    self.successes.value += 1
            else:
                with self.failures.get_lock():
                    self.failures.value += 1
