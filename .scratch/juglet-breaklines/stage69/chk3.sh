RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0734_601013e_t69-density-panel
echo '=== job5 proof section ==='; grep -n 'proof\|pg_run\|geomid' $RUN/submit.sbatch | head -40
echo '=== potd progress ==='; tail -4 $RUN/logs/slurm-34274535.out
