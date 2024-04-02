#!/usr/bin/env python3

import subprocess
import shlex
from tempfile import mktemp
import multiprocessing
import argparse

# This is to execute arbitrary command with
# - exeute a thread with the command
# - stream stdout and stderr of the thread to a file
# - return the file name to the user and exit while the thread is still running


def execute_command(command, foutname):
    with open(foutname, 'a+') as fout:
        command_split = shlex.split(command)
        try:
            popen = subprocess.Popen(command_split, stdout=fout, stderr=fout, bufsize=1)
        except Exception as e:
            print(f"# {e}", file=fout)
            print(f'#end {foutname}', file=fout)
            return
        popen.wait()
        print(f'#end {foutname}', file=fout)


def process_input(command):
    foutname = mktemp()
    with open(foutname, 'w') as fout:
        print(f'#begin {command} {foutname}', file=fout)
    # execute command in a separate process and quit
    process = multiprocessing.Process(target=execute_command, args=(command, foutname))
    process.start()
    return foutname


def main():
    argparser = argparse.ArgumentParser(description='Execute command and stream output to file')
    argparser.add_argument('command', nargs=argparse.REMAINDER, help='Command to execute')
    args = argparser.parse_args()
    cmnd = ' '.join(args.command)
    out = process_input(cmnd)
    print(out)


if __name__ == '__main__':
    main()
