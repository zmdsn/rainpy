#!/usr/bin/env python3

import argparse
import os
import datetime
from .raindrop import *

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

