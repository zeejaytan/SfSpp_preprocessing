#!/bin/bash
#SBATCH --job-name=p155_v6
#SBATCH --output=p155_v6.log
#SBATCH --error=p155_v6.err
#SBATCH --time=01:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=4
#SBATCH --partition=sapphire

module load Apptainer
SIF=/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif
SUB=/data/gpfs/projects/punim2657/sfs_cure_1c6a8f9/original_nurbs_preprocessing
TREE=/data/gpfs/projects/punim2657/sfs_cure_1c6a8f9
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PRODBIN=/data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing/build/EdgeLineExtractionHeadless

mkdir -p $TREE/pair_cure && cp $SUB/Dataset/Breaklines/Pot_A/* $TREE/pair_cure/ 2>/dev/null
echo "===== BASELINE re-run (same staged surfaces) ====="
$APT exec --bind /data:/data $SIF bash -c "cd $SUB && $PRODBIN > $TREE/run_base6.log 2>&1; echo BASE-RUN-EXIT:$?"
mkdir -p $TREE/pair_base && cp $SUB/Dataset/Breaklines/Pot_A/* $TREE/pair_base/

echo "===== PAIR COUNTS (cure vs base, per piece) ====="
cd $TREE
for f in pair_cure/*.pcd; do b=$(basename $f); echo "CURE $b: $(grep -c . $TREE/pair_cure/$b 2>/dev/null) / BASE $b: $(grep -c . $TREE/pair_base/$b 2>/dev/null)"; done
cp $TREE/pair_cure/* $SUB/Dataset/Breaklines/Pot_A/ 2>/dev/null
echo "===== DONE (cured outputs restored) ====="
