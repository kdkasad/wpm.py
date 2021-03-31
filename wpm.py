#!/usr/bin/env python

"""
wpm.py - typing speed test
Copyright (C) 2021  Kian Kasad

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import json
import platform
import random
import termios
from sys import stdin, stdout, argv
from time import time
from math import ceil, floor
from os import get_terminal_size

def get_random_text():
    """
    Get a random text from texts.json
    """
    list = []
    with open('texts.json', 'r') as file:
        list = json.load(file)
    return random.choice(list)[0]

def disable_raw_mode():
    """
    Disable raw input mode
    """

    # returned structure is [iflag, oflag, cflag, lflag, ispeed, ospeed, cc]
    tattr = termios.tcgetattr(stdin.fileno())
    tattr[3] |= (termios.ECHO | termios.ICANON)
    termios.tcsetattr(stdin.fileno(), termios.TCSAFLUSH, tattr)


def enable_raw_mode():
    """
    Enable raw input mode

    In raw input mode, each character is send to the program as soon as it is
    typed; all console line editing is disabled
    """

    # returned structure is [iflag, oflag, cflag, lflag, ispeed, ospeed, cc]
    tattr = termios.tcgetattr(stdin.fileno())
    tattr[3] &= ~(termios.ECHO | termios.ICANON)
    termios.tcsetattr(stdin.fileno(), termios.TCSAFLUSH, tattr)

def print_help():
    help_text = \
    """
wpm - typing speed test

Usage:
    PROGNAME [options] [text...]

    Options:
        -h, --help      print usage information

    Text:
        any positional arguments will be combined into a string which
        will be used as the text to type
    """.strip().replace("PROGNAME", argv[0])
    print(help_text)

def print_with_template(template, overlay):
    """
    Print text overlayed on a template
    """

    print('\033[1;32m', end='')
    for i in range(len(overlay)):
        if template[i] == overlay[i]:
            print(template[i], end='')
        else:
            char = template[i]
            if char == ' ':
                char = '_'
            print('\033[1;31m' + char + '\033[1;32m', end='')

    print('\033[m', end='')
    print(template[len(overlay):])
    # print('\033[1;32m' + template[:len(overlay)] + '\033[m' + template[len(overlay):])

def main():
    # Check for help flags
    if len(argv) > 1 and (argv[1] == '-h' or argv[1] == '--help'):
        print_help()
        exit()

    # Check OS
    if platform.system() != 'Linux':
        print('Only Linux is supported currently')

    # get text
    text = ''
    if len(argv) > 1:
        text = " ".join(argv[1:])
    else:
        text = get_random_text()

    # user has not typed anything yet
    typed = ''

    enable_raw_mode()

    # initialize timer
    start_time = 0

    # program loop
    while True:
        # calculate cursor movement
        width, _ = get_terminal_size(stdout.fileno())
        linesup = ceil(len(text) / width)
        linesdown = floor(len(typed) / width)
        charsover = len(typed) % width

        # clear line
        print('\r\033[2K', end='')

        # print text
        print_with_template(text, typed)

        # print elapsed time
        elapsed_time = (time() - start_time if start_time != 0 else 0)
        print('\033[2B\r\033[2K', end='')
        print('{}s'.format(round(elapsed_time, 2)), end='')
        print('\033[2A', end='')

        # move cursor to next untyped letter
        if linesup - linesdown > 0:
            print('\033[{}F\r'.format(linesup - linesdown), end='')
        if charsover > 0:
            print('\033[{}C'.format(charsover), end='')

        if typed == text:
            break

        # read one character
        c = stdin.read(1)

        # start timer on first letter
        if start_time == 0:
            start_time = time()

        # if character is a backspace, delete one character from `typed`
        if c == chr(127):
            typed = typed[:-1]
        # otherwise, append the character to `typed`
        else:
            typed += c
        
        # move back to start of text
        if linesdown > 0:
            print('\033[{}A'.format(linesdown), end='')
    
    # stop timer
    end_time = time()
    time_elapsed = end_time - start_time

    # count words in text
    words = len(text.split(" "))
    
    disable_raw_mode()

    # print information
    print('\n')
    print("Words typed: {}".format(words))
    print("Time elapsed: {} seconds".format(round(time_elapsed, 2)))
    print("Words per minute: {}".format(round(words / (time_elapsed / 60))))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
