#!/bin/bash
#SBATCH --job-name=t67b-attitude
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# submit67b.sbatch -- ticket 67 job 2 (task 3, the attitude attack). Same run dir as job 1
# (RUN=$SLURM_SUBMIT_DIR); reuses job 1's include roots, staged trees and pristine build.
# Arms: A20 = Juglet floor 20 on the instrumented guarded shim; APA = Pot A floor 50 on the same
# instrumented source (convention calibration: GT pairs there must read near-zero pose error).
set -uo pipefail

RUN=$SLURM_SUBMIT_DIR
MAIN=/data/gpfs/projects/punim2657/sfs_main
SIF=$MAIN/sfs_pristine_assembly.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
WORK=$RUN/work
OUT=$RUN/out
TREES=$RUN/trees
LOG=$RUN/logs
INS=$RUN/instruments

cp $INS/arm67.sh $WORK/arm67.sh
echo "=== t67b job $SLURM_JOB_ID on $(hostname) at $(date -u +%FT%TZ)"
md5sum $INS/* > $LOG/provenance_b.log

$PY $INS/patch_attitude67.py $WORK/shim/G.cpp $WORK/shim/GA.cpp > $LOG/attitude.log 2>&1
ARC=$?
diff -u $WORK/shim/G.cpp $WORK/shim/GA.cpp > $LOG/diff_attitude.txt
md5sum $WORK/shim/G.cpp $WORK/shim/GA.cpp >> $LOG/attitude.log
cat $LOG/attitude.log
if [ $ARC -ne 0 ]; then echo "!!!! attitude patch failed rc=$ARC"; exit 4; fi

runarm () {
  ARM=$1; FLOOR=$2; INC=$3; TREE=$4; NP=$5; EXTRA=$6
  T0=$SECONDS
  echo "##### LAUNCH $ARM floor=$FLOOR tree=$TREE"
  $APT exec --writable-tmpfs \
     --bind $MAIN:/workspace --bind $WORK:/panel --bind $OUT:/out --bind $TREE:/Dataset/SfS_pp \
     $SIF bash /panel/arm67.sh $ARM $FLOOR $INC $NP $EXTRA /panel/shim/GA.cpp >> $LOG/panel_b.log 2>&1
  RC=$?
  DT=$((SECONDS - T0))
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$ARM" "$FLOOR" "$INC" "$TREE" "$NP" "$EXTRA" "$RC" "$DT" >> $LOG/panel.tsv
  echo "##### $ARM exit=$RC wall=$DT sec"
  return 0
}

runarm A20 20 /panel/inc1 $TREES/juglet 9 -DJUGLET_ORIG
runarm APA 50 /panel/inc2 $TREES/pota   8 NONE

md5sum $WORK/shim/A20.cpp $WORK/shim/APA.cpp $WORK/build/Hierarchy-A20 $WORK/build/Hierarchy-APA 2>/dev/null | tee -a $LOG/md5_binaries.txt
cp $WORK/logs/binary_A20.log $WORK/logs/binary_APA.log $WORK/logs/diff_A20.txt $WORK/logs/diff_APA.txt $LOG/ 2>/dev/null
for ARM in A20 APA; do
  echo "[$ARM]"; cat "$OUT/$ARM/1. Acc.txt" 2>/dev/null
  wc -l $OUT/$ARM/T67_*.tsv 2>/dev/null
done
echo "=== t67b job finished $(date -u +%FT%TZ)"
