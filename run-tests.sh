#!/usr/bin/env bash

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 [skipped-tests] [srcdir]"
  exit 1
fi

SKIPS="$1"
SRCDIR="$2"

PASS="pass"
FAIL="fail"
touch $PASS $FAIL

while read -r fname; do
  if [[ "$fname" =~ ^#.*$ ]]; then
    continue
  fi

  echo -n "Running ${fname}... "
  (
    cd $SRCDIR
    mach mochitest $fname --enable-fission --headless --timeout=15 >/dev/null 2>&1
  )

  if [ $? -eq 0 ]; then
    echo $PASS
    echo $fname >> $PASS
  else
    echo $FAIL
    echo $fname >> $FAIL
  fi
done < "$SKIPS"
