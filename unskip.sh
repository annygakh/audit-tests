# Input - `filename of the test` `directory` `skiplist[optional]`

TEST_FILENAME=$(basename "$1")

DIR="$2"

if [ "$#" -ge 3 ]; then
    SKIPLIST="$3"
    grep $TEST_FILENAME $SKIPLIST
    if [ $? -eq 0 ]; then
      # We found this test in unexpected failure test. So don't change the annotation
      echo "Skipping test " $TEST_FILENAME
      exit 0
    fi
fi
echo "test filename=" $TEST_FILENAME

# Get the name of the ini file
INI_FNAME=$(rg --glob "*.ini" -l $TEST_FILENAME $DIR)

# rg --glob "*.ini" -l browser_largeAllocation_non_win32.js
# echo "ini filename=" $INI_FNAME -
# Search for the line number where 'fission' is contained in the above INI file
LINE_NUM=$(rg --glob "*.ini" -A 10 --no-filename --line-number $TEST_FILENAME $DIR | grep fission -m 1 | cut -f 1 -d ":" | cut -f 1 -d "-")
echo "line number=" $LINE_NUM
if [ -z "$LINE_NUM" ]
then
  echo "line number for test is empty, don't change annotation. also this is weird"
  exit 0
fi
# echo ""
# Change words `fission` to `false`
# echo sed -i "" -e "${LINE_NUM}s/fission/false/" $INI_FNAME
sed -i "" -e "${LINE_NUM}s/fission/false/" $INI_FNAME
