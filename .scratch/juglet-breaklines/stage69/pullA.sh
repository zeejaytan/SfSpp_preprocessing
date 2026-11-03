set -euo pipefail
BR=69-axis-density-corpus-check
CAN=/data/gpfs/projects/punim2657/sfs_preprocessing
W=/data/gpfs/projects/punim2657/SfSpp/scratch69
git -C $CAN fetch -q origin $BR
C=$(git -C $CAN rev-parse FETCH_HEAD)
echo COMMIT $C
rm -rf $W/sfs_axes
git -C $CAN archive $C sfs_axes | tar -x -C $W
ls $W/sfs_axes
git -C $CAN show $C:.scratch/juglet-breaklines/stage69/partA69.py > $W/partA69.py
md5sum $W/partA69.py
