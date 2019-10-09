# For each test we have in our unskipped tests
# - We want to skip the test
# - We want to run the test
# - If the test ends cleanly, log it tests well done test
# - If the


# ----- Constants
bold=$(tput bold)
normal=$(tput sgr0)
CLEAN_TESTS="clean_tests"
FAILED_TESTS="failed_tests"

SKIPPED_TESTS="$1"
CODE_DIR="$2"
if [ "$#" -lt 2 ]; then
  echo "Usage:" $0 "[file with skipped tests] [code directory]"
  exit 1
fi
echo $SKIPPED_TESTS
echo $CODE_DIR
while read -r TEST_FNAME; do
    echo "${bold}Removed test annotation for ${TEST_FNAME} ${normal}"
    ./unskip.sh $TEST_FNAME $CODE_DIR
    echo "${bold}Running the test ${TEST_FNAME} ${normal}"
    cd $CODE_DIR
    mach mochitest $TEST_FNAME --enable-fission --timeout=20 --headless
    SUCCESS=$?
    git checkout -- .
    echo "${bold}Undoing annotation changes${normal}"
    cd -
    if [ $SUCCESS -eq 0 ]; then
      echo $TEST_FNAME >> $CLEAN_TESTS
      echo "${bold}Test - SUCCESS ${normal}"
    else
      echo $TEST_FNAME >> $FAILED_TESTS
      echo "${bold}Test - FAIL ${normal}"
    fi
done < "$SKIPPED_TESTS"
