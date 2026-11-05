#!/bin/bash
R=/data/gpfs/projects/punim2657/SfSpp/runs
sacct -j 34372619,34372620,34372621,34372622,34372623,34372624,34372625,34372626,34372627,34372628,34372629,34372630,34372673 --format=JobID%14,State,ExitCode,Elapsed --noheader | grep -v '[.]'
echo "== acc so far"
for d in $R/*_e6adf69_t307-*-np8; do
  [ -s $d/score/acc.tsv ] && { echo "-- $(basename $d)"; tail -n +2 $d/score/acc.tsv; }
done
