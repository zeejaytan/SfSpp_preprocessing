RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2351_3888318_p291-gate
echo ===STAGE_H02===
cat $RUN/out/stage_H02.log
echo ===STAGE_J09===
cat $RUN/out/stage_J09.log
echo ===IDX===
grep p291 /data/gpfs/projects/punim2657/SfSpp/runs/index.tsv
echo ===OUT_LIST===
ls $RUN/out
