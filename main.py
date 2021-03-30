import platform
import sys
import termios
from os import get_terminal_size
from math import ceil, floor

def finish():
    disable_raw_mode()
    print()
    print("You're done!")

def disable_raw_mode():
    """
    Disable raw input mode
    """

    # returned structure is [iflag, oflag, cflag, lflag, ispeed, ospeed, cc]
    tattr = termios.tcgetattr(sys.stdin.fileno())
    tattr[3] |= (termios.ECHO | termios.ICANON)
    termios.tcsetattr(sys.stdin.fileno(), termios.TCSAFLUSH, tattr)


def enable_raw_mode():
    """
    Enable raw input mode

    In raw input mode, each character is send to the program as soon as it is
    typed; all console line editing is disabled
    """

    # returned structure is [iflag, oflag, cflag, lflag, ispeed, ospeed, cc]
    tattr = termios.tcgetattr(sys.stdin.fileno())
    tattr[3] &= ~(termios.ECHO | termios.ICANON)
    termios.tcsetattr(sys.stdin.fileno(), termios.TCSAFLUSH, tattr)

def print_with_template(template, overlay):
    """
    Print text overlayed on a template
    """

    print('\033[1;32m', end='')
    for i in range(len(overlay)):
        if template[i] == overlay[i]:
            print(template[i], end='')
        else:
            print('\033[1;31m' + template[i] + '\033[1;32m', end='')

    print('\033[m', end='')
    print(template[len(overlay):])
    # print('\033[1;32m' + template[:len(overlay)] + '\033[m' + template[len(overlay):])

def main():
    # Check OS
    if platform.system() != 'Linux':
        print('Only Linux is supported currently')

    TEXT = 'make also she hand but only off each great same must such head \
present might of those down end who good stand also govern help during which \
down great fact tell change be such'

    # user has not typed anything yet
    typed = ''

    enable_raw_mode()

    # program loop
    while True:
        # calculate cursor movement
        width, _ = get_terminal_size(sys.stdout.fileno())
        linesup = ceil(len(TEXT) / width)
        linesdown = floor(len(typed) / width)
        charsover = len(typed) % width

        # clear line
        print('\r\033[2K', end='')

        # print text
        print_with_template(TEXT, typed)

        # move cursor to next untyped letter
        if linesup - linesdown > 0:
            print('\033[{}F\r'.format(linesup - linesdown), end='')
        if charsover > 0:
            print('\033[{}C'.format(charsover), end='')

        if typed == TEXT:
            break

        # read one character
        c = sys.stdin.read(1)

        # if character is a backspace, delete one character from `typed`
        if c == chr(127):
            typed = typed[:-1]
        # otherwise, append the character to `typed`
        else:
            typed += c
        
        # move back to start of text
        if linesdown > 0:
            print('\033[{}A'.format(linesdown), end='')
    
    finish()

if __name__ == '__main__':
    main()