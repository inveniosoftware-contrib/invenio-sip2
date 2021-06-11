# -*- coding: utf-8 -*-
#
# INVENIO-SIP2
# Copyright (C) 2020 UCLouvain
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Invenio module that add SIP2 communication for self-check"""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    "mock>=2.0.0",
    "pytest-mock>=1.6.0",
    'check-manifest>=0.35',
    'coverage>=4.5.3',
    'invenio-app>=1.2.3',
    'invenio-db>=1.0.4',
    'autoflake>=1.3.1',
    'isort>=5.1.0',
    'pydocstyle>=5.0.0',
    'pytest>=4.6.4,<6.0.0',
    'pytest-cache>=1.0',
    'pytest-cov>=2.7.1',
    'pytest-pep8>=1.0.6',
    'pytest-invenio>=1.2.2,<1.4.0'
]

invenio_search_version = '1.2.1'
invenio_db_version = '1.0.4'

extras_require = {
    'elasticsearch6': [
        'invenio-search[elasticsearch6]>={}'.format(invenio_search_version),
    ],
    'elasticsearch7': [
        'invenio-search[elasticsearch7]>={}'.format(invenio_search_version),
    ],
    'docs': [
        'Sphinx>=3',
    ],
    'mysql': [
        'invenio-db[versioning,mysql]>={}'.format(invenio_db_version),
    ],
    'postgresql': [
        'invenio-db[versioning,postgresql]>={}'.format(invenio_db_version),
    ],
    'sqlite': [
        'invenio-db[versioning]>={}'.format(invenio_db_version),
    ],
    'tests': tests_require,
}

extras_require['all'] = []

for name, reqs in extras_require.items():
    if name in (
        'mysql',
        'postgresql',
        'sqlite',
        'elasticsearch6',
        'elasticsearch7',
    ):
        continue
    extras_require['all'].extend(reqs)

setup_requires = [
    'Babel>=1.3',
    'pytest-runner>=3.0.0,<5',
]

install_requires = [
    'cachelib>=0.1',
    'cryptography>=2.1.4',
    'Flask-BabelEx>=0.9.4',
    'Flask-Security>=3.0.0',
    'Flask-Login>=0.4.0,<0.5.0',
    'email-validator>=1.0.5',
    'six>=1.12.0',
    'SQLAlchemy>=1.2.18,<1.4.0',
    'SQLAlchemy-Utils>=0.33.1,<0.36',
    'invenio-base>=1.2.3',
    'invenio-access>=1.3.1',
    'pycountry>=19.7.15',
    'jsonpickle>=1.2',
    'psutil>=5.8.0',
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('invenio_sip2', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='invenio-sip2',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='invenio SIP2',
    license='AGPL',
    author='UCLouvain',
    author_email='laurent.dubois@uclouvain.be',
    url='https://github.com/inveniosoftware-contrib/invenio-sip2',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'invenio_base.apps': [
            'invenio_sip2 = invenio_sip2:InvenioSIP2',
        ],
        'invenio_base.api_apps': [
            'invenio_sip2 = invenio_sip2:InvenioSIP2',
        ],
        'invenio_base.blueprints': [
            'invenio_sip2 = invenio_sip2.views.views:blueprint',
        ],
        'invenio_base.api_blueprints': [
            'invenio_sip2 = invenio_sip2.views.rest:api_blueprint',
        ],
        'flask.commands': [
            'selfcheck = invenio_sip2.cli:selfcheck'
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU AFFERO GENERAL PUBLIC LICENSE V3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Development Status :: 3 - Alpha',
    ],
)
