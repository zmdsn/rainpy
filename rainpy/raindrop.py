#!/usr/bin/env python3

import argparse
import os
import datetime

py_head = """#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""

sh_head = """#!/bin/sh 
"""

BSD_3 = """
Copyright {year} {author}

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

set_up = py_head + """
# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages

with open('README.md', encoding="utf-8") as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='{name}',
    version='0.1.0',
    description='description for Sample package',
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

tests_init = py_head + """
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import {name}
"""

start_sh = sh_head + """
cd {folder}

pip install ipython
pip install pipenv
pip install pytest
pip install ipykernel

echo python --version
echo "install all success"

git config --global user.name {name}
git config --global user.email {email}
rm -rf .git
git init
git add .
git commit -m "generate by rainpy"
"""

test_sh = sh_head + """
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
*.pyc
.venv
.vscode
.pytest_cache
"""

test_example = py_head + """
import pytest
import {name}

def test_passing():
    assert (1, 2, 3) == (1, 2, 3)
"""


def make_foleder(path):
    if not os.path.exists(path):
        os.makedirs(path)


def make_file(path, content, mode="w"):
    with open(path, mode) as f:
        f.write(content)


licenes = {"BSD": BSD_3}


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
    file_path = os.path.join(args.floder, "setup.py")
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


def make_require_sh(args):
    file_path = os.path.join(args.floder, "make_require.sh")
    make_file(file_path, make_require)


def make_test_sh(args):
    file_path = os.path.join(args.floder, "test.sh")
    make_file(file_path, test_sh)


def make_ignore(args):
    file_path = os.path.join(args.floder, ".gitignore")
    make_file(file_path, gitignore_list)


def make_test_exm(args):
    test_example_content = test_example.format(name=args.name)
    file_path = os.path.join(args.floder, "tests", f"test_{args.name}.py")
    make_file(file_path, test_example_content)


class make_web:
    run_py = """
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
"""
    blue_print = """
from flask import Blueprint

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return 'Hello, World!'
"""
    app = """
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    from . import routes
    app.register_blueprint(routes.bp)

    return app"""
    def __init__(self, name) -> None:
        self.name = name
    

    def make_web(self):
        pass

def make_folders(folder, sub_forlders, folder_lists):
    for sub_folder in folder_lists:
        sub_path = os.path.join(folder, sub_forlders, sub_folder)
        make_foleder(sub_path)


def make_files(folder, sub_forlders, file_lists, content=""):
    for file in file_lists:
        file_path = os.path.join(folder, sub_forlders, file)
        make_file(file_path, content)

def make_frame(args):
    folder = args.floder
    make_foleder(folder)
    make_folders(folder, "", [".venv", "doc", "tests", args.name])
    make_license(args)
    make_setup(args)
    make_read_me(args)
    make_tests_init(args)
    make_require_sh(args)
    make_test_sh(args)
    make_ignore(args)
    make_test_exm(args)

    make_files(folder, "", ["requirements.txt", "lab.ipynb"])
    make_files(folder, args.name, ["__init__.py", "utils.py"])
    make_files(folder, sub_forlders="", file_lists=["__init__.py", "utils.py"])

    make_start(args)

    if args.web:
        web_maker = make_web(args.web)
        make_folders(folder, args.name, ["routes", "models", "templates", "static"])
        make_files(folder, "", ["config.py"])
        make_files(folder, "", ["run.py"], web_maker.run_py)
        make_files(folder, args.name, ["__init__.py"], web_maker.app)

        make_files(folder, f"{args.name}/routes", ["__init__.py"])
        make_files(folder, f"{args.name}/routes", ["main.py"], web_maker.blue_print)
        make_files(folder, f"{args.name}/templates", ["__init__.py"])
        make_files(folder, f"{args.name}/models", ["__init__.py"])
        web_maker.make_web()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='argparse testing')
    parser.add_argument('--name', '-n', type=str, default="raindrop",
                        required=True, help="Your python package name")
    parser.add_argument('--floder', '-f', type=str, default="./raindrop",
                        required=True, help='The folder you want to put in')
    parser.add_argument('--author', '-a', type=str,
                        required=True, default="zmdsn", help='your name')
    parser.add_argument('--email', '-e', type=str,
                        required=True, default="zmdsn@126.com",  help='your email')
    parser.add_argument('--url', '-u', type=str,
                        default="", help='the url in git')
    parser.add_argument('--web', '-w', type=str,
                        default="", help='falsk/faskapi')
    args = parser.parse_args()
    make_frame(args)


# export PATH=$PATH:xx
# raindrop.py --name app --floder example -a zmdsn -e zmdsn@126.com
