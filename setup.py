#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.md') as history_file:
    history = history_file.read()

install_requirements = [
    'coloredlogs',
    'Flask==1.0.2',
    'Flask-Cors==3.0.6',
    'flask-swagger==0.2.14',
    'flask-swagger-ui==3.20.9',
    'Jinja2>=2.10.1',
    'kubernetes==10.0.0',
    'requests>=2.21.0',
    'gunicorn==19.9.0',
    'PyYAML==5.1',
    'pytz',
]

setup_requirements = ['pytest-runner',]

dev_requirements = [
    'bumpversion',
    'pkginfo',
    'twine',
    'watchdog',
]

test_requirements = [
    'coverage',
    'mccabe',
    'pylint',
    'pytest'
]

setup(
    author="Keyko",
    author_email='root@keyko.io',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Infrastructure Operator Micro-service",
    extras_require={
        'test': test_requirements,
        'dev': dev_requirements + test_requirements,
    },
    include_package_data=True,
    install_requires=install_requirements,
    keywords='nevermined-compute-api',
    license="Apache Software License 2.0",
    long_description=readme,
    long_description_content_type="text/markdown",
    name='nevermined-compute-api',
    packages=find_packages(include=['nevermined_compute_api']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/keyko-io/nevermined-compute-api',
    version='0.1.0',
    zip_safe=False,
)
