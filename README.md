## Get pathnames of all tests that are currently being skipped
1. Download [fission.csv](https://docs.google.com/spreadsheets/d/1kjp32JTuB4axM3wKx0iIYL2Ado-HcyeBhoY-siGxYAs/edit#gid=1560718888)
2. Extract a list of skipped tests for either 'opt' or 'debug'
`python3 get_skipped_tests.py fission.csv opt skipped_opt`
- pipe the above through `grep` filters to remove tests that we are not working on currently, e.g. 'remote' or 'devtools'

## Identify which tests have a clean shutdown locally
3. On a machine, run this script overnight, unskipping each test individually and seeing if there is a clean shutdown
`./unskip_individually.sh skipped_opt [code directory]`
- this will produce test files 'clean_tests' and 'failed_tests'
- 'clean_tests' - pathnames of tests with clean shutdown
- 'failed_tests' - problems with shutdown

## Unskip all tests from clean_tests and push to try for the first time
4. Unskip all tests
`cat clean_tests | xargs -L 1 -I F ./unskip.sh "F" [code directory]`
- this will change `fission` keyword to `false` in `.ini` files for each test in 'clean_tests'
5. Push to try for the first time

## Inspect try failures and add annotations back for failing tests
6. Get names of tests with unexpected failures from Task Cluster
- Run the following in javascript console after selecting `tbody` to `use in console`
```
var childs = temp1.children;
for (var i = 0; i < childs.length; i++) {
  if (childs[i].children[0].textContent != "failed") continue;
  var task_links = childs[i].children[1].children[0].href;
  console.log(task_links);
}
```

- Download the output into file and delete extra text (requires some vim macros). Now we have task links - `task_links.txt`
```
https://tools.taskcluster.net/groups/ZGpoarrNTlC2AnNoz-z-Iw/tasks/EZis_ClyRZi_ufUQDJM7CA/details
...
https://tools.taskcluster.net/groups/ZGpoarrNTlC2AnNoz-z-Iw/tasks/RzJyaS17R_a45bPu5E6SoA/details
```

- Construct raw log links from task links (vim magic) - `log_links.txt`
```
https://taskcluster-artifacts.net/EZis_ClyRZi_ufUQDJM7CA/0/public/logs/live_backing.log
...
https://taskcluster-artifacts.net/RzJyaS17R_a45bPu5E6SoA/0/public/logs/live_backing.log
```

- Download all the raw logs into a folder
```
mkdir logs && cd logs
cat log_links.txt | xargs -K 1 wget
```
- `in logs directory` Convert log files to have `gz` extension so we can gunzip them
```
for file in *.log
do
  mv "$file" "$(basename "$file" .log).gz"
done
```
- `in logs directory` Gunzip all of the logs so they are plain text
ls | xargs gunzip
- Now we need to grep the logs for "TEST-UNEXPECTED-FAIL" and get filenames of tests
`rg "TEST-UNEXPECTED-FAIL" --no-filename | cut -f 2 -d "|" | cut -d ' ' -f 2 | sort -u > unexpected_fail`
7. Append unexpected_fail to a previous version if you already run step 6 before.
8. Now add back all skip annotations (i.e. undoing all your earlier changes) and only unskip those that are not in `unexpected_fail`

  `cat clean_tests | xargs -L 1 -I F ./unskip.sh "F" [code directory] unexpected_fail`
9. Push to try
10. Repeat steps 6-10 until your unexpected_fail test stops changing

## Identify tests that are not failing but causing other tests to fail

11. At some point you might have test failures that are a side effect from other tests that were running in the test suite. This will need to be dealt with manually. Repeat steps 12-TODO for every try job you have.

12. Download raw logs for the try job

12. Extract a list of test pathnames that were run/skipped in a specific try running
`grep "TEST-START" logs.log | cut -f 12 -d ' ' | sort -u > tests_run_or_skipped_try_job`

13. Gather a list of `.ini` files that were modified while adding annotations
`git diff --name-only --stat -U1 <commit before you added the skips> <latest commit on the branch that has all your skips>  -- '*.ini'   > ini_files_changed_skips`

14. Gather a list of test files that were skipped by us in an test suite that has other failing tests. Add back annotations for those (manually).
`python3 cross_search_tests.py tests_run_or_skipped_try_job ini_files_changed_skips [repo]`
