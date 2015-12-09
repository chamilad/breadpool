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
# import traceback
import logging
import time

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class _WorkerThread(Thread):
    def __init__(self, task_queue, thread_name, polling_timeout):
        super(_WorkerThread, self).__init__(name=thread_name)
        self.__task_queue = task_queue
        """ :type : Queue """
        self.__terminated = False
        """ :type : bool """
        self.__thread_name = thread_name
        """ :type : str """
        self.__polling_timeout = polling_timeout
        """ :type : int """

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
                if isinstance(task, AbstractRunnable):
                    try:
                        task.execute()
                    except BaseException as ex:
                        log.info("Caught exception while executing task : %s: %s" % (ex.__class__.__name__, ex))
                        # traceback.print_exc()

                    # notify the queue that the task is done
                    self.__task_queue.task_done()
                else:
                    # this should not happen!
                    log.error("Invalid object enqueued to task list.")

        log.debug("Terminating worker thread %s" % self.__thread_name)

    def terminate(self):
        self.__terminated = True


class ThreadPool(object):
    def __init__(self, size, name, daemon=False, polling_timeout=60):
        if size == 0:
            raise ValueError("Thread pool size should be more than 0")

        self.__task_queue = Queue()
        """ :type : Queue """
        self.__pool_size = size
        """ :type : int """
        self.__pool_name = name
        """ :type : str """
        self.__worker_threads = []
        """ :type : list """
        self.__polling_timeout = polling_timeout
        """ :type : int """
        self.__daemon = daemon
        """ :type : bool """""

        self.create_worker_threads()

    def enqueue(self, task):
        if not isinstance(task, AbstractRunnable):
            raise ValueError("The task must be of AbstractRunnable or a subclass of it.")

        # thread safety comes from Queue class
        self.__task_queue.put(task)

    def get_pool_size(self):
        with rLock():
            return self.__pool_size

    def terminate(self):
        with rLock():
            log.debug("Waiting until all the tasks are done")
            self.__task_queue.join()
            log.debug("Sending termination signal for the worker threads")
            for worker_thread in self.__worker_threads:
                worker_thread.terminate()

    def create_worker_threads(self):
        with rLock():
            while len(self.__worker_threads) < self.__pool_size:
                thread_name = "%s-%s" % (self.__pool_name, (len(self.__worker_threads) + 1))
                worker_thread = _WorkerThread(self.__task_queue, thread_name, self.__polling_timeout)
                worker_thread.setDaemon(self.__daemon)
                worker_thread.start()
                self.__worker_threads.append(worker_thread)


class ScheduledJobExecutor(Thread):
    """
    A Scheduled executor which periodically executes a given task.
    """
    def __init__(self, task, thread_pool, delay, name):
        super(ScheduledJobExecutor, self).__init__()
        self.__task = task
        """ :type : AbstractRunnable """
        self.__thread_pool = thread_pool
        """ :type : ThreadPool  """
        self.__delay = delay
        """ :type : int """
        self.__terminated = False
        """ :type : bool """
        self.__name = name
        """ :type : str """

        self.setName(name)

    def run(self):
        # start job
        while not self.__terminated:
            start_time = time.time()
            with rLock():
                # sleep for the required duration if lock acquisition took time
                if not self.__terminated:
                    lock_end_time = time.time()
                    remaining_wait_time = self.__delay - (lock_end_time - start_time)
                    if remaining_wait_time > 0.0:
                        time.sleep(remaining_wait_time)

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


class EasyTask(AbstractRunnable):
    """
    An implementation of the AbstractRunnable class which accepts a function to be executed.
    """
    def execute(self):
        log.debug("Executing [function] %s" % self.function.__name__)
        self.function(*self.args, **self.kwargs)

    def __init__(self, function, *args, **kwargs):
        if not hasattr(function, '__call__'):
            raise ValueError("The task is not a valid function")

        self.function = function
        self.args = args
        self.kwargs = kwargs
