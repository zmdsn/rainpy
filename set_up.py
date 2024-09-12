
# -*- coding: utf-8 -*-
# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='rainpy',
    version='0.0.2',
    description='Work tools',
    long_description=readme,
    author='zmdsn',
    author_email='zmdsn@126.com',
    url='',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
