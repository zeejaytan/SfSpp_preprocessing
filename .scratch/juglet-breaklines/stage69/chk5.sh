RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0734_601013e_t69-density-panel
ls $RUN/
echo '--- instruments ---'; ls $RUN/instruments 2>/dev/null
echo '--- SIF line 37 context ---'; sed -n '30,45p' $RUN/submit.sbatch
