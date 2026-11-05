#!/bin/bash
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
RUN=$RUNS/20261105-0422_e6adf69_t307d-jug
printf '%s\t%s\te6adf69\t%s\t\t\n' "20261105-0422_e6adf69_t307d-jug" "34372673" "t307d-jug-r2" > $RUN/index_row_r2.tsv
cat $RUN/index_row_r2.tsv >> $RUNS/index.tsv
echo "== jug r2 row"; cat $RUN/index_row_r2.tsv
echo "== states"
sacct -j 34372619,34372620,34372621,34372622,34372623,34372624,34372625,34372626,34372627,34372628,34372629,34372630,34372673 --format=JobID%14,State,ExitCode,Elapsed --noheader | grep -v '[.]'
