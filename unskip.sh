#!/usr/bin/env bash

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 [input file] [srcdir]"
  exit 1
fi

FNAME="$1"
SRCDIR="$2"

TESTDIR=$(dirname $FNAME)
TESTFILE=$(basename $FNAME)

for NAME in "browser.ini" "mochitest.ini"; do
  INIFILE="$SRCDIR/$TESTDIR/$NAME"

  if [ ! -f "$INIFILE" ]; then
    continue
  fi

  LINE=$(
    rg -A10 --no-filename --line-number -e $TESTFILE $INIFILE |
    grep -m1 fission |
    cut -d: -f1 |
    cut -d- -f1
  )

  echo -n "Unskipping $FNAME... "

  if [ ! -z $LINE ]; then
    sed -e "${LINE}s/fission/false/" -i $INIFILE
    echo "done"
  else
    echo "already done"
  fi
done
