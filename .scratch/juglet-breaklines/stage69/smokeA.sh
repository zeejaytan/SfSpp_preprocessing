set -uo pipefail
cd /data/gpfs/projects/punim2657
W=/data/gpfs/projects/punim2657/SfSpp/scratch69
mkdir -p $W
C=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
time $PY $W/partA69.py $C $W/smoke_G --pots G --jobs 4 2>&1 | tail -40
