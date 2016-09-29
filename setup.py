#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'requests',
    'stups-tokens',
    'click',
    'clickclick',
    'environmental>=1.0',
]

test_requirements = [
    'pytest',
    'mock'
]

setup(
    name='metricz',
    version='0.1.4',
    description="Metricz makes it easy to write metrics to a Kairosdb instance running with OAuth2 security.",
    long_description=readme + '\n\n' + history,
    author="Daniël Franke",
    author_email='daniel.franke@zalando.de',
    url='https://github.com/zalando-incubator/metricz',
    packages=[
        'metricz',
    ],
    package_dir={'metricz':
                 'metricz'},
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='metricz',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    setup_requires=['pytest-runner'],
    tests_require=test_requirements,
    entry_points={'console_scripts': ['metricz = metricz.cli:main']}
)
