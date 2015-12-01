# Copyright 2015 Chamila de Alwis
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from Queue import Queue, Empty
from threading import Thread, RLock as rLock
import traceback
import logging
import time

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler)


class _WorkerThread(Thread):
    def __init__(self, task_queue, thread_name, polling_timeout):
        super(_WorkerThread, self).__init__(name=thread_name)
        self.__task_queue = task_queue
        """ :type : Queue """
        self.__terminated = False
        self.__thread_name = thread_name
        self.__polling_timeout = polling_timeout

    def run(self):
        while not self.__terminated:
            # locking implemented by the Queue class
            # blocks until a task is queued
            task = None
            try:
                task = self.__task_queue.get(timeout=self.__polling_timeout)
            except Empty:
                pass

            if task is not None:
                log.info("Work!")
                # print "Work!!"
                try:
                    task.execute()
                except Exception as ex:
                    log.info("Caught exception while executing task : %s" % ex.message)
                    # print "Caught exception while executing task : %s" % ex.message
                    traceback.print_exc()

                    # notify the queue that the task is done
                self.__task_queue.task_done()

        log.debug("Terminating worker thread %s" % self.__thread_name)
        # print "Terminating worker thread %s" % self.__thread_name

    def terminate(self):
        self.__terminated = True


class ThreadPool(object):
    def __init__(self, size, name, daemon=False, polling_timeout=60):
        if size == 0:
            raise ValueError("Thread pool size should be more than 0")

        self.__task_queue = Queue()
        self.__pool_size = size
        self.__pool_name = name
        self.__worker_threads = []
        self.__polling_timeout = polling_timeout
        self.__daemon = daemon
        self.create_worker_threads()

    def enqueue(self, task):
        # thread safety comes from Queue class
        self.__task_queue.put(task)

    def get_pool_size(self):
        return self.__pool_size

    def terminate(self):
        log.debug("Waiting until all the tasks are done")
        # print "Waiting until all the tasks are done"
        self.__task_queue.join()
        log.debug("Sending termination signal for the worker threads")
        # print "Sending termination signal for the worker threads"
        for worker_thread in self.__worker_threads:
            worker_thread.terminate()

    def create_worker_threads(self):
        while len(self.__worker_threads) < self.__pool_size:
            thread_name = "%s-%s" % (self.__pool_name, (len(self.__worker_threads) + 1))
            worker_thread = _WorkerThread(self.__task_queue, thread_name, self.__polling_timeout)
            worker_thread.setDaemon(self.__daemon)
            worker_thread.start()
            self.__worker_threads.append(worker_thread)
            # print "Worker thread created %s" % thread_name


class ScheduledJobExecutor(Thread):
    def __init__(self, task, thread_pool, delay):
        super(ScheduledJobExecutor, self).__init__()
        self.__task = task
        """ :type : AbstractRunnable """
        self.__thread_pool = thread_pool
        """ :type : ThreadPool  """
        self.__delay = delay
        self.__terminated = False

    def run(self):
        # start job
        while not self.__terminated:
            with rLock():
                time.sleep(self.__delay)
                if not self.__terminated:
                    self.__thread_pool.enqueue(self.__task)

    def terminate(self):
        with rLock():
            self.__terminated = True
            self.__thread_pool.terminate()


class AbstractRunnable(object):
    """
    Extend AbstractRunnable to implement the task to be run.
    """

    def __init__(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError
