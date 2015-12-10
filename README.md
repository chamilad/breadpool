[![Build Status](https://travis-ci.org/chamilad/breadpool.svg?branch=master)](https://travis-ci.org/chamilad/breadpool) 
[![Coverage Status](https://coveralls.io/repos/chamilad/breadpool/badge.svg?branch=master&service=github?dd=gg)](https://coveralls.io/github/chamilad/breadpool?branch=master)
[![Documentation Status](https://readthedocs.org/projects/breadpool/badge/?version=latest)](http://breadpool.readthedocs.org/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/breadpool.svg)](https://badge.fury.io/py/breadpool)

# BreadPool 
##A Python Thread Pool and a Scheduled Executor

BreadPool intends to simply provide implementations for a thread pool and a scheduled executor, with
easy to use interfaces and thread safety. Yes, it is a simple code to write your own implementations
for these, however it can be a lot easier if they come in a `pip install`.

## Installing BreadPool
BreadPool can be installed from the Python Package Index.

```bash
pip install breadpool
```

## ThreadPool
The `ThreadPool` class is a simple thread pool implementation. It will initially create a set of worker threads and when assigned tasks, the worker threads will take over and execute the tasks.

### Creating a ThreadPool

```python
from breadpool.pool import ThreadPool

"""
1 - number of threads to spawn
2 - An identifying name to be assigned to the threads
3 - daemon, True if you want the threads to immediately terminate when the main thread terminates. This is set to False by default
4 - polling_timeout is the timeout for the worker threads to blockingly wait for the task queue
"""
thread_pool = ThreadPool(5, "CustomThreadPool", polling_timeout=1)

```

### Enqueuing tasks
The tasks should be implemented by extending the `AbstractRunnable` class. BreadPool provides a simple implementation of the `AbstractRunnable` class called `EasyTask` which accepts a function as the task to be executed.

```python
from breadpool.pool import ThreadPool, EasyTask

def func_test():
    time.sleep(random.randint(1, 5))
et = EasyTask(func_test)
thread_pool = ThreadPool(5, "CustomThreadPool", daemon=True)
thread_pool.enqueue(et)
```

### Extending `AbstractRunnable`
Or if your task is too complex for a simple function, you can extend the `AbstractRunnable` class and write your own task implementation.

```python
from breadpool.pool import AbstractRunnable

class CustomTask(AbstractRunnable):
    def execute(self):
        # task steps

    def __init__(self):
        # task initialization

```

## ScheduledJobExecutor
This is a simple scheduled executor for tasks of type `AbstractRunnable`. It will periodically and repeatedly execute the given task with at least the given time interval.

### Usage

```python
from breadpool.pool import ThreadPool, ScheduledJobExecutor, EasyTask

thread_pool = ThreadPool(3, "CustomThreadPool", polling_timeout=20)
counter_queue = Queue()
scheduled_executor = ScheduledJobExecutor(
    EasyTask(lambda(l): counter_queue.put(l), "Test %s" % time.time()),
    thread_pool,
    5,
    "CustomScheduledExecutor")

scheduled_executor.start()
....
scheduled_executor.terminate()
```

## Python Support
BreadPool supports only Python 2.7 (for now).

## License
BreadPool is an Apache v2.0 licensed project. 

## Additional Links

1. ReadTheDocs - http://breadpool.readthedocs.org/en/latest/
2. PyPI - https://pypi.python.org/pypi/breadpool

