set -uo pipefail
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1733_45ba206_t69-axis-corpus
W=$RUN/work
mkdir -p $W
cp -r /data/gpfs/projects/punim2657/SfSpp/scratch69/sfs_axes $W/
cp /data/gpfs/projects/punim2657/SfSpp/scratch69/partA69.py $W/
ls -l $W $W/sfs_axes | head -30
md5sum $W/partA69.py
echo ---SACCT---
sacct -j 34273111 -P -o JobID,JobName,State,ExitCode,Elapsed,MaxRSS
