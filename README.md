## audit-tests

Scripts to audit skipped tests for Fission.

#### Unskip tests locally

1. Download the "fission-tests-status" sheet as a csv from [here](https://docs.google.com/spreadsheets/d/1kjp32JTuB4axM3wKx0iIYL2Ado-HcyeBhoY-siGxYAs/edit#gid=2031736766).
1. Run `get_skipped_tests.py` with that csv as input. The 2nd argument will filter skipped tests based on their build.

    ```console
    $ ./get_skipped_tests.py fission-tests-status.csv [opt|debug]
    ```

    This will print a list of skipped tests to stdout.
1. Use `unskip.sh` to unskip tests locally.

    ```console
    $ cat skipped-tests | xargs -n1 -I{} ./unskip.sh {} /path/to/mozilla-central
    ```

1. You can use `run-tests.sh` to run the tests locally to confirm that they're actually passing. This step will take time and is mostly optional. It may avoid running unnecessary tests on try.

    ```console
    $ ./run-tests.sh skipped-tests /path/to/mozilla-central
    ```

1. If you ran the tests locally, you should now have 2 new files: `pass` and `fail`. Tests in the `fail` file are still failing locally, so they shouldn't be unskipped. Use `reskip.sh` to update their annotations.

    ```console
    $ cat fail | xargs -n1 -I{} ./reskip.sh {} /path/to/mozilla-central
    ```

#### Push to try

1. Commit the changes.

    ```console
    $ cd /path/to/mozilla-central
    $ hg commit -m "Unskip fission tests" -m "$(cat /path/to/skipped-tests)"
    ```

1. Push to try. There's many ways to do this. The following runs the unskipped tests 3 times on an artifact build. When the fuzzy chooser shows up, filter on `"-fis-"` and select all jobs.

    ```console
    $ cat /path/to/skipped-tests | xargs mach try fuzzy --rebuild 3 --artifact
    ```

#### Analyze try results

The try push will take _some_ time. After it's done you can use the scripts in `analyze/` to fetch and parse test logs.

```console
$ cd analyze/
$ ./fetch_logs.py 'https://treeherder.mozilla.org/#/jobs?repo=try&revision=$REVISION' logs/
$ ./check_logs.py logs/*.log
```

This will print tests that failed or timed out. You can manually go through this list and run `reskip.sh` to re-add the skip annotation for tests that are still failing. You should now have a list of tests that are no longer failing and can be unskipped permanantely. You'll need to manually go through this list and remove the "skip-if = false" annotations. There's generally not that many tests to update at this point, so it shouldn't take long, but scripts to automate this would be nice.
