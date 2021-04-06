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
    'Flask==1.1.2',
    'Flask-Cors==3.0.8',
    'flask-swagger==0.2.14',
    'flask-swagger-ui==3.20.9',
    'Jinja2>=2.10.1',
    'argo-workflows-fvdnabee',
    'kubernetes~=11.0',
    'requests>=2.21.0',
    'gunicorn==19.9.0',
    'PyYAML==5.3',
    'pytz',
    'web3==5.9.0',
    'nevermined-sdk-py==0.9.0rc0',
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
    'pytest',
    'pytest-mock==3.2.0',
]

setup(
    author="Keyko",
    author_email='root@nevermined.io',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
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
    url='https://github.com/nevermined-io/compute-api',
    version='0.3.0',
    zip_safe=False,
    package_data={'nevermined_compute_api': ['*.yaml']}
)
