#!/bin/bash

total=0

for f in Dataset/Breaklines/Pot_A/*.pcd; do
    count=$(grep "^# [0-9]" "$f" | wc -l)
    segments=$((count - 2))
    echo "$(basename $f): $segments segments"
    total=$((total + segments))
done

echo ""
echo "Total segments: $total"
echo "Sample dataset total: 56 segments"
echo "Difference: $((total - 56)) segments"
