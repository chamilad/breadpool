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

import threading
from breadpool.pool import *


def get_threads_with_name(thread_name):
    live_threads = threading.enumerate()
    named_threads = {}
    for live_thread in live_threads:
        if thread_name in live_thread.name:
            named_threads[live_thread.name] = live_thread

    return named_threads


class TestTask(AbstractRunnable):
    def execute(self):
        self.task(self.args)

    def __init__(self, task, *args):
        self.args = args
        self.task = task
