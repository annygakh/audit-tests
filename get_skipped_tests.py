#!/usr/bin/env python3

import sys
import csv

INDEXES = {"opt": 1, "debug": 2}


def process(filename, status):
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for row in csv_reader:
            if len(row) < 1:
                continue
            if row[INDEXES[status]] == "skipped":
                sys.stdout.write(row[0] + "\n")


if __name__ == "__main__":
    usage = f"Usage: {sys.argv[0]} [fission-tests-status.csv] [opt|debug]"
    if len(sys.argv) < 3 or sys.argv[2] not in INDEXES:
        print(usage)
        sys.exit(1)
    process(sys.argv[1], sys.argv[2])
