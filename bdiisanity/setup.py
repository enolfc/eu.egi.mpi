# vim: tabstop=4 shiftwidth=4 softtabstop=4

#
# Copyright (c) 2014, Spanish National Research Council
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from setuptools import setup

setup(
    name='mpimetrics',
    version='0.1.0',
    description='eu.egi.mpi SAM package',
    long_description=("This package includes the metrics for the eu.egi.mpi"
                      "for testing MPI support in the EGI.eu infrastructure."),
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta'
        'Topic :: System :: Systems Administration',
    ],
    keywords='',
    author='Spanish National Research Council',
    author_email='enolfc@ifca.unican.es',
    url='https://github.com/IFCA/eu.egi.mpi',
    license='Apache License, Version 2.0',
    include_package_data=True,
    packages=['mpimetrics'],
    zip_safe=False,
    entry_points = {
        'console_scripts': [
            'checkbdii = mpimetrics.shell:main',
        ]
    },
)
