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
import datetime
import time
from breadpool.pool import *
import util

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
    live_threads = util.get_threads_with_name("TestThreadPoolSize")

    assert len(live_threads.keys()) == 5
    thread_pool.terminate()


def test_thread_pool_polling_timeout():
    thread_pool = ThreadPool(5, "TestThreadPoolPolling", polling_timeout=5)
    while len(util.get_threads_with_name("TestThreadPoolPolling").keys()) < 5:
        time.sleep(0.5)

    before_time = datetime.datetime.now()
    # print before_time.time()
    thread_pool.terminate()
    while len(util.get_threads_with_name("TestThreadPoolPolling").keys()) > 4:
        time.sleep(0.5)

    after_time = datetime.datetime.now()
    # print after_time.time()
    diff_time = after_time - before_time
    print diff_time.seconds
    # assert False
    assert diff_time.seconds == 5


def test_thread_pool_daemon_flag():
    thread_pool = ThreadPool(2, "TestThreadPoolDaemonFlag", daemon=True, polling_timeout=1)
    created_threads = util.get_threads_with_name("TestThreadPoolDaemonFlag")
    # print len(created_threads)
    thread_name, thread_obj = created_threads.popitem()
    assert thread_obj.daemon is True
    thread_pool.terminate()


def test_thread_pool_thread_limitation():
    global counter_queue
    thread_pool = ThreadPool(5, "TestThreadPoolLimitation", polling_timeout=1)
    i = 0
    counter_queue = Queue()
    while i < 10:
        thread_pool.enqueue(util.TestTask(lambda(l): counter_queue.put(l), "Test%s" % i))
        i += 1

    assert len(util.get_threads_with_name("TestThreadPoolLimitation")) == 5
    thread_pool.terminate()
    assert counter_queue.qsize() == 10
