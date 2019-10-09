import sys
import os

'''
1. We have a list of tests (fullpath) that were run/skipped in a specific try running
$ grep "TEST-START" logs.log | cut -f 12 -d ' ' | sort -u

2. We have a list of ini files that were modified in my commits
git diff --name-only --stat -U1 c7893bd772ecee1bed69878fa78faa211e64eb07 all_skips  -- '*.ini'   > ini_files_changed_skips

3. We need to process it here.
'''

def search(tests, inis, repo):
    dir_tests = {}
    dir_inis = {}
    process_file(tests, dir_tests)
    process_file(inis, dir_inis)
    os.chdir(repo)
    for dirname, ini_files in dir_inis.items(): # We are iterating over dirnames of ini files
        # We might have several ini files in the same dirname, browser.ini and mochitest.ini
        if not dirname in dir_tests:
            print(f'No tests ran from ini files: {ini_files}')
            continue
        else:
            print(f'Perhaps see {dir_inis[dirname]} tests')
            continue
        for ini_fname in ini_files:
            # All test that are in this directory
            tests_in_dirname = dir_tests[dirname]
            # Read the ini file and see if we have tests within it
            print(f'Looking at directory: {dirname}')
            with open(ini_fname) as ini_file:
                print(f'looking at file: {ini_fname}')
                ini_contents = ini_file.read()

                for test_path in tests_in_dirname:
                    test_basename = os.path.basename(test_path)
                    if test_basename in ini_contents:
                        print(f'\tFound this test: {test_basename}')
                    else:
                        print(f'\tCould not find test: {test_basename}')

def process_file(file, pairings):
    for path in file:
        dirname = os.path.dirname(path).rstrip()
        if not dirname in pairings:
            # Create a new list
            pairings[dirname] = []
        pairings[dirname].append(path.rstrip())


if __name__ == '__main__':
    tests_run_from_log_file = open(sys.argv[1], "r")
    ini_files_modified_in_commit_file = open(sys.argv[2], "r")
    repo = sys.argv[3]

    search(tests_run_from_log_file, ini_files_modified_in_commit_file, repo)
