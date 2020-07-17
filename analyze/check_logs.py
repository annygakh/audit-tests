#!/usr/bin/env python3
# vim:se sts=4 sw=4 et fenc=utf-8 ft=python:
import json
import re
import sys


class Test(object):
    def __init__(self, name, is_debug):
        self.name = name

        self.errors = []
        self.failures = []
        self.crashes = []
        self.logs = []

        self.is_debug = is_debug

        self.timed_out = False

    @property
    def failed(self):
        return len(self.failures) > 0 or len(self.crashes) > 0


tests = []
crashes = []

current_test = None

pat = re.compile("PageStyleChild.*cross-origin")
pat = re.compile("LinkHandlerChild.*cross-origin")
pat = re.compile("ContentSessionStore.*cross-origin")
pat = re.compile("LoginManagerContent.*cross-origin")
pat = re.compile("getCachedMessages.*cross-origin")
matches = set()

for fn in sys.argv[1:]:
    with open(fn) as fh:
        is_debug = False

        for line in fh:
            if not line:
                continue

            log = json.loads(line)

            if log["action"] == "test_start":
                current_test = Test(log["test"], is_debug)
                tests.append(current_test)
            elif log["action"] == "test_end":
                current_test = None
            else:
                if not is_debug and log["action"] == "process_output":
                    if log["data"].startswith("++DOCSHELL"):
                        is_debug = True
                        if current_test:
                            current_test.is_debug = True

                if current_test:
                    current_test.logs.append(log)

                    if log["action"] == "process_output":
                        if "JavaScript error" in log["data"]:
                            if pat.search(log["data"]):
                                matches.add(current_test.name)
                            current_test.errors.append(log)
                    elif log["action"] == "test_status":
                        failed = log["status"] != log.get("expected", "PASS")
                        if failed:
                            current_test.failures.append(log)
                            if log["subtest"] == "Test timed out":
                                current_test.timed_out = True

                if log["action"] == "crash":
                    if current_test:
                        current_test.crashes.append(log)

                    crashes.append(log)

tests_passed = 0
tests_failed = 0
tests_crashed = 0

debug_crashes = set()
opt_crashes = set()

for test in tests:
    if test.crashes:
        if test.is_debug:
            debug_crashes.add(test.name)
        else:
            opt_crashes.add(test.name)

for test in tests:
    if test.crashes:
        tests_crashed += 1
    elif test.failures:
        tests_failed += 1
    else:
        tests_passed += 1

    if not test.timed_out and test.failures:
        print("T:", test.name)
    elif test.crashes:
        if test.is_debug:
            if test.name in opt_crashes:
                print("C:", test.name, test.crashes[0]["signature"])
            else:
                print("D:", test.name, test.crashes[0]["signature"])
        elif test.name not in debug_crashes:
            print("C:", test.name, test.crashes[0]["signature"])
    elif test.timed_out:
        print("Z:", test.name)

    if test.failed and test.errors:
        print("Test: %s" % test.name)
        for error in test.errors:
            print("  ", error["data"])
        print("")

print("Total:   %d" % len(tests))
print("Passed:  %d" % tests_passed)
print("Failed:  %d" % tests_failed)
print("Crashed: %d" % tests_crashed)

print("")
print("Matching tests: %d" % len(matches))
