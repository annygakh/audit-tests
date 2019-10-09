
# some bits from initial attempt to document all instructions

# --------------- Getting names of unexpected tests that failed from TaskCluster ---------
# 1. Run the following in javascript console after selecting tbody to `use in console`
var childs = temp1.children;
for (var i = 0; i < childs.length; i++) {
  if (childs[i].children[0].textContent != "failed") continue;
  var task_links = childs[i].children[1].children[0].href;
  console.log(task_links);
}
# 1.1 Download the above into a file and delete extra text. Now we have task links - task_links.txt

# 2. Construct raw log links from task links (vim magic most likely) - log_links.txt

# 3. Download all the raw logs into a folder
mkdir logs && cd logs
cat log_links.txt | xargs -K 1 wget

# 3.1. `in logs directory`  Convert log files to have `gz` extension so we can gunzip them

```
for file in *.log
do
  mv "$file" "$(basename "$file" .log).gz"
done
```

# 3.2. `in logs directory` Gunzip all of the logs so they are plain text
ls | xargs gunzip


# Now we need to grep the logs for "TEST-UNEXPECTED-FAIL" and get filenames of tests
rg "TEST-UNEXPECTED-FAIL" --no-filename | cut -f 2 -d "|" | cut -d ' ' -f 2 | sort -u > unexpected_fail

# ---------------- Getting names of tests we have skipped from the spreadsheet-------------
# 1. Download fission.csv from the spreadsheet
# 2. Run the python test
python3 get_skipped_tests.py > skipped

# ---------------- Unskipping only tests that don't cause any issues
# Now I attempt to skip all tests that we want to skip with exception of these
cat ./skipped | xargs -L 1 -I F ./unskip.sh "F" central/ ./unexpected_fail

# ----------- Unskipping individually
./unskip_individually.sh skipped ash/

#
