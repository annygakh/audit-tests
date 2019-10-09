LOG_NAME="$1"
REPO="$2"

FNAME="tests"

grep "TEST-START" $LOG_NAME | cut -f 12 -d ' ' | sort -u > $FNAME

python3 cross_search_tests.py $FNAME ini_files_changed_skips $2
