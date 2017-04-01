#!/usr/bin/env python

import json
import sys


def main():
    with open(sys.argv[1]) as f:
        data = [json.loads(line) for line in f]
    


if __name__ == '__main__':
    main()