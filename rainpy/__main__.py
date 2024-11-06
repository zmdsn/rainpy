#!/usr/bin/env python3
# for run in console 
import argparse
import os
import datetime
from .raindrop import make_frame
from .run_func import run_func

def main():
    parser = argparse.ArgumentParser(description='argparse testing')
    parser.add_argument('--name', '-n', type=str, default="raindrop",
                        required=True, help="Your python package name")
    parser.add_argument('--floder', '-f', type=str, default="",
                        required=True, help='The folder you want to put in')
    parser.add_argument('--author', '-a', type=str,
                        required=True, default="zmdsn", help='your name')
    parser.add_argument('--email', '-e', type=str,
                        required=True, default="zmdsn@126.com",  
                        help='your email')
    parser.add_argument('--url', '-u', type=str,
                        default="", help='the url in git')
    parser.add_argument('--web', '-w', type=str,
                        default="", help='falsk or faskapi')
    # for run func
    parser.add_argument('--run', '-r', type=str,
                        default="", help='The func to run')
    parser.add_argument('--file', '-f', type=str,
                        default="", help='The origin file')
    parser.add_argument('--save', '-s', type=str,
                        default="", help='The file or folder to save')

    args = parser.parse_args()
    if "run" in args:
        run_func(args)
    else:
        make_frame(args)

if __name__ == "__main__":
    main()
