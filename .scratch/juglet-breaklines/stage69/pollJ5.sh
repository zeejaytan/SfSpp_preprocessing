J=34274535
sacct -j $J -P -o JobID,JobName,State,ExitCode,Elapsed,MaxRSS 2>&1
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0734_601013e_t69-density-panel
echo '--- rows ---'; wc -l $RUN/out_pota/pieces.tsv $RUN/out_potc/pieces.tsv $RUN/out_potd/pieces.tsv $RUN/out_potj/pieces.tsv 2>/dev/null
echo '--- tail joblog ---'; tail -20 $RUN/logs/*.out 2>/dev/null | tail -25
