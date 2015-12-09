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

import pytest
import logging
from testfixtures import log_capture
import random
import threading

from ..pool import *
from ..pool import _WorkerThread  # 100% coverage
import testutil

"""
ThreadPool
"""


def test_thread_pool_value_exception():
    with pytest.raises(ValueError):
        ThreadPool(0, "TestThreadPoolValException")


def test_thread_pool_value_property():
    thread_pool = ThreadPool(5, "TestThreadPoolValueProperty", polling_timeout=1)
    assert thread_pool.get_pool_size() == 5
    thread_pool.terminate()


def test_thread_pool_pool_thread_size():
    thread_pool = ThreadPool(5, "TestThreadPoolSize", polling_timeout=1)
    live_threads = testutil.get_threads_with_name("TestThreadPoolSize")

    assert len(live_threads.keys()) == 5
    thread_pool.terminate()


def test_thread_pool_daemon_flag():
    thread_pool = ThreadPool(2, "TestThreadPoolDaemonFlag", daemon=True, polling_timeout=1)
    created_threads = testutil.get_threads_with_name("TestThreadPoolDaemonFlag")
    # print len(created_threads)
    thread_name, thread_obj = created_threads.popitem()
    assert thread_obj.daemon is True
    thread_pool.terminate()


def test_thread_pool_thread_limitation():
    thread_pool = ThreadPool(5, "TestThreadPoolLimitation", polling_timeout=1)
    i = 0
    counter_queue = Queue()
    while i < 10:
        thread_pool.enqueue(EasyTask(lambda(l): counter_queue.put(l), "Test%s" % i))
        i += 1

    assert len(testutil.get_threads_with_name("TestThreadPoolLimitation")) == 5
    thread_pool.terminate()
    assert counter_queue.qsize() == 10


def test_thread_pool_task_validation():
    thread_pool = ThreadPool(1, "TestThreadPoolTaskValidation", daemon=True, polling_timeout=1)
    with pytest.raises(ValueError):
        thread_pool.enqueue("dd")

    thread_pool.terminate()

"""
ScheduledJobExecutor
"""


def test_scheduled_executor_scheduling():
    thread_pool = ThreadPool(3, "TestScheduledExecutorScheduling", polling_timeout=1)
    counter_queue = Queue()
    scheduled_executor = ScheduledJobExecutor(
        EasyTask(lambda(l): counter_queue.put(l), "STest %s" % time.time()),
        thread_pool,
        5,
        "TestSchedulingScheduledExecutor")

    scheduled_executor.start()
    time.sleep(27)
    scheduled_executor.terminate()
    assert counter_queue.qsize() == 5


def test_scheduled_executor_thread_limit():
    def wait_test_task():
        time.sleep(random.randint(10, 30))

    thread_pool = ThreadPool(5, "TestScheduledExecutorThreadLimit", polling_timeout=60, daemon=True)
    scheduled_executor = ScheduledJobExecutor(
        EasyTask(wait_test_task),
        thread_pool,
        1,
        "TestThreadLimitScheduledExecutor"
    )

    scheduled_executor.start()
    time.sleep(10)

    testutil.print_all_active_threads()
    assert threading.activeCount() == (5 + 1 + 1)  # worker threads + main thread + scheduled executor thread
    scheduled_executor.terminate()

"""
EasyTask
"""


def test_easy_task_validation():
    with pytest.raises(ValueError):
        EasyTask("dd")

"""
_WorkerThread
"""


@log_capture(level=logging.ERROR)
def test_worker_thread_task_validation(l):
    test_queue = Queue(maxsize=4)
    worker_thread = _WorkerThread(test_queue, "TestWorkerThreadTaskValidation", 10)
    worker_thread.setDaemon(True)
    worker_thread.start()

    test_queue.put("dd")
    time.sleep(5)
    l.uninstall()
    l.check(('breadpool.pool', 'ERROR', 'Invalid object enqueued to task list.'),)

    worker_thread.terminate()


@log_capture(level=logging.INFO)
def test_worker_thread_task_execution_exception_handling(lg):
    thread_pool = ThreadPool(1, "TestWorkThreadTaskException", daemon=True, polling_timeout=10)

    def raising(lll):
        raise ValueError("Some Exception %s" % lll)

    thread_pool.enqueue(EasyTask(raising, "Exception caught"))
    time.sleep(3)
    lg.uninstall()
    lg.check((
        'breadpool.pool',
        'INFO',
        'Caught exception while executing task : ValueError: Some Exception Exception caught'),)

    thread_pool.terminate()

"""
AbstractRunnable
"""


def test_abstract_runnable_non_creation():
    with pytest.raises(NotImplementedError):
        AbstractRunnable()


def test_abstract_runnable_non_execution():

    class NotWorkingRunnable(AbstractRunnable):
        def __init__(self):
            pass

        def execute(self):
            AbstractRunnable.execute(self)

    test_worker = NotWorkingRunnable()
    with pytest.raises(NotImplementedError):
        test_worker.execute()
