# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='breadpool',
      version='0.0.5',
      description='A Python Thread Pool and a Scheduled Executor',
      url='https://github.com/chamilad/breadpool',
      author='Chamila de Alwis',
      author_email='cs@chamiladealwis.com',
      license='Apache v2.0',
      packages=['breadpool'],
      install_requires=[],
      zip_safe=False,
      long_description=read('README.md'),
      keywords="python thread pool scheduled executor",
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: Apache Software License",
          "Natural Language :: English",
          "Operating System :: Unix",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Libraries",
      ],
      test_suite='breadpool.tests.test_pool',
      tests_require=['pytest'],
      include_package_data=True,)
