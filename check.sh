#!/bin/sh

MAX_COLS=80
MAX_LINES=60

awk -v max="$MAX_COLS" '
length($0) > max {
    printf "ERROR: line %d is %d columns (max %d)\n", NR, length($0), max
    bad=1
}
END { exit bad }
' resume.txt || exit 1

lines=$(wc -l <resume.txt)

if [ "$lines" -gt "$MAX_LINES" ]; then
  echo "ERROR: $lines lines (max $MAX_LINES)"
  exit 1
fi

echo "OK: ${MAX_COLS}x${MAX_LINES} bounds respected"
