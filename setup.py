
# -*- coding: utf-8 -*-
# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages

with open('README.md', encoding="utf-8") as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='rainpy',
    version='v0.12.04',
    description='Work tools',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='zmdsn',
    author_email='zmdsn@126.com',
    url='',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
