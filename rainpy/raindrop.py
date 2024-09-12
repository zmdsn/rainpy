#!/usr/bin/env python3
 
import argparse
import os
import datetime



BSD_3 = """
Copyright {year} {author}

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

set_up = """
# -*- coding: utf-8 -*-
# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='{name}',
    version='0.1.0',
    description='Sample package',
    long_description=readme,
    author='{author}',
    author_email='{email}',
    url='{url}',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
"""

read_me = """
# {name}

This simple project is an example of a rainpy project build.

[Learn more](https://github.com/zmdsn/rainpy)
"""

tests_init = """
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import {name}
"""

start_sh = """
cd {folder}

pip install ipython
pip install pipenv
pip install pytest

echo python --version
echo "install all success"

git config user.name {name}
git config user.email {email}
rm -rf .git
git init
git add .
git commit -m "generate by rainpy"
"""

test_sh = """
mkdir .venv

pip install pipenv
pip install pytest-cov
pip install pytest-html
pip install pytest-xdist
pipenv --three

pipenv run pip3 install -r requirements.txt #  -i xxx --trusted-host xxx
echo "install all success"

# 执行 并 统计覆盖率
pipenv run pytest --cov=. --cov-report=html:reports/coverage_report --cov-config=.coveragerc --html=reports/testresult.html --self-contained-html
""" 

make_require = "pipreqs ./ --encoding UTF8 --force --use-local --ignore .venv"

gitignore_list = """
.coverage
reports/
"""

def make_foleder(path):
    if not os.path.exists(path):
        os.makedirs(path)

def make_file(path, content, mode="w"):
    with open(path,mode) as f:
        f.write(content)


licenes = {"BSD":BSD_3}

def get_year():
    now = datetime.datetime.now()
    return now.year

def make_license(args):
    license = BSD_3.format(year=get_year(), author=args.author)
    file_path = os.path.join(args.floder, "LICENSE")
    make_file(file_path, license)

def make_setup(args):
    set_up_content = set_up.format(name=args.name,
                            author=args.author,
                            email=args.email,
                            url=args.url)
    file_path = os.path.join(args.floder, "set_up.py")
    make_file(file_path, set_up_content)

def make_read_me(args):
    read_me_content = read_me.format(name=args.name)
    file_path = os.path.join(args.floder, "README.md")
    make_file(file_path, read_me_content)

def make_tests_init(args):
    tests_init_content = tests_init.format(name=args.name)
    file_path = os.path.join(args.floder, "tests", "__init__.py")
    make_file(file_path, tests_init_content)

def make_start(args):
    start_sh_content = start_sh.format(folder=args.floder,
                                       name=args.name,
                                 email=args.email)
    file_path = os.path.join(args.floder, "start.sh")
    make_file(file_path, start_sh_content)
    os.system(f"sh {file_path}")


def make_req():
    file_path = os.path.join(args.floder, "make_require.sh")
    make_file(file_path, make_require)


def make_req():
    file_path = os.path.join(args.floder, "test.sh")
    make_file(file_path, test_sh)

def make_ignore():
    file_path = os.path.join(args.floder, ".gitignore")
    make_file(file_path, test_sh)


def make_frame(args):
    folder = args.floder
    make_foleder(folder)
    for sub_folder in [".venv", "doc", "tests", args.name]:
        sub_path = os.path.join(folder, sub_folder)
        make_foleder(sub_path)
        
    make_license(args)
    make_setup(args)
    make_read_me(args)
    make_tests_init(args)
    make_req()
    make_ignore()
    
    for file in [".gitignore", "requirements.txt", "lab.ipynb"]:
        file_path = os.path.join(folder, file)
        make_file(file_path, "")

    for file in ["__init__.py", "core.py", "utils.py"]:
        file_path = os.path.join(folder, args.name, file)
        make_file(file_path, "")
    make_start(args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='argparse testing')
    parser.add_argument('--name','-n',type=str, default = "raindrop", required=True,help="Your python package name")
    parser.add_argument('--floder','-f',type=str, default="./raindrop", required=True, help='The folder you want to put in')
    parser.add_argument('--author','-a',type=str, default="zmdsn" , help='your name')
    parser.add_argument('--email','-e',type=str, default="zmdsn@126.com",  help='your email')
    parser.add_argument('--url','-u',type=str, default="", help='the url in git')
    args = parser.parse_args()
    make_frame(args)
    
    
# export PATH=$PATH:xx
# raindrop.py --name ss --floder  -a zmdsn -e zmdsn@126.com
