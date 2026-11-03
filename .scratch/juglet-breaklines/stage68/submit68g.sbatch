#!/bin/bash
#SBATCH --job-name=t68g-guard-proof
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
# submit68g.sbatch -- ticket 68 Part B proof-build (budget job 4).
# The canonical guard patch (instruments/guard68.patch) is applied with git apply to a git-archive COPY
# of the assembler at cc1d859 taken read-only from sfs_main/sfspreproc-docker; the copy is cold-built
# (cmake+make, class/ranking_system.cpp patched) and the patched hpc/tools/main_pristine_batch.cpp is
# linked in place of main.cpp.o exactly as arm67.sh does, with /opt/sfs-pristine replaced by the copy.
# NO t67 shim guard (patch_guard67.py) is used: the only guard is the canonical patch.
#   GJ50  Juglet, floor 50, staged t68 bundle (t66 lanes + t68 axes) -> expect SFS-NO-CANDIDATES, exit 0
#   GPA50 Pot A,  floor 50                                           -> expect 8/8 and 15/15
# Submitted FROM $RUN (= job-1 run dir/guard68). Appends no index row.
set -uo pipefail

RUN=$SLURM_SUBMIT_DIR
COMMIT=cc1d859
LANES=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom
DS=/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset
POTA=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
MAIN=/data/gpfs/projects/punim2657/sfs_main
SIF=$MAIN/sfs_pristine_assembly.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
WORK=$RUN/work
SRC=$WORK/src
OUT=$RUN/out
TREES=$RUN/trees
LOG=$RUN/logs
INS=$RUN/instruments

mkdir -p $WORK/inc1/class $WORK/inc2/class $WORK/shim $WORK/logs $WORK/build $SRC $OUT $TREES $LOG
echo "=== t68g job $SLURM_JOB_ID on $(hostname) at $(date -u +%FT%TZ)"

# ---------- source copy + patch ----------
{
  echo "--- canonical checkout (read only)"
  git -C $MAIN/sfspreproc-docker rev-parse HEAD
  git -C $MAIN/sfspreproc-docker rev-parse --verify $COMMIT^{commit}
  git -C $MAIN/sfspreproc-docker status --porcelain | head
} > $LOG/provenance.log 2>&1
git -C $MAIN/sfspreproc-docker archive $COMMIT | tar x -C $SRC
if [ ! -f $SRC/class/ranking_system.cpp ]; then echo "!!!! archive of $COMMIT failed"; exit 6; fi
cd $SRC
git init -q && git add -A && git -c user.email=t68@local -c user.name=t68 commit -qm "archive $COMMIT"
# guard68.patch was cut against the laptop's CRLF (autocrlf) checkout; the blobs are LF (job 34269496
# failed git apply on that alone), so the LF copy of the same patch is what applies to the archive.
tr -d '\r' < $INS/guard68.patch > $WORK/guard68.lf.patch
git apply --check $WORK/guard68.lf.patch && git apply $WORK/guard68.lf.patch
ARC=$?
{
  echo "--- patch md5 crlf $(md5sum $INS/guard68.patch | cut -d' ' -f1)  lf $(md5sum $WORK/guard68.lf.patch | cut -d' ' -f1)"
  echo "--- git apply rc=$ARC"
  echo "--- applied tree vs archive (numstat):"
  git diff --numstat
  echo "--- files changed: $(git diff --name-only | wc -l)  insertions/deletions:"
  git diff --shortstat
  echo "--- applied diff == patch hunks? (diff of +/- lines, empty = identical)"
  diff <(git diff | grep -E '^[-+]' | grep -vE '^(\+\+\+|---)') <(grep -E '^[-+]' $WORK/guard68.lf.patch | grep -vE '^(\+\+\+|---)') && echo "IDENTICAL"
  echo "--- patch md5 $(md5sum $INS/guard68.patch | cut -d' ' -f1)"
  md5sum class/ranking_system.cpp main.cpp hpc/tools/main_pristine_batch.cpp class/data_path.h
} > $LOG/apply.log 2>&1
cat $LOG/apply.log
cd $RUN
if [ $ARC -ne 0 ]; then echo "!!!! git apply failed"; exit 7; fi
cp $SRC/hpc/tools/main_pristine_batch.cpp $WORK/shim/P.cpp

# ---------- arm script: arm67.sh with the patched copy in place of /opt/sfs-pristine ----------
sed -e 's|/opt/sfs-pristine|/src|g' $INS/arm67.sh > $WORK/arm68g.sh
diff $INS/arm67.sh $WORK/arm68g.sh > $LOG/diff_arm.txt
chmod +x $WORK/arm68g.sh

# ---------- include roots (t58/t67 recipe) ----------
$APT exec $SIF cat /opt/sfs-pristine/class/data_path.h > $WORK/inc2/class/data_path.h 2>>$LOG/provenance.log
cp $WORK/inc2/class/data_path.h $WORK/inc1/class/data_path.h
sed -i 's/^#define POT_A$/#define POT_A_INFRA_OFF_JUGLET/' $WORK/inc1/class/data_path.h
cp $INS/juglet_orig_block.inc $WORK/juglet_orig_block.inc
cat $WORK/juglet_orig_block.inc >> $WORK/inc1/class/data_path.h
{
  echo "--- pristine (SIF) vs archive, class/ and main sources (informational):"
  $APT exec --bind $SRC:/src $SIF bash -c 'for f in /src/class/*.cpp /src/class/*.h /src/main.cpp; do b=${f#/src/}; cmp -s $f /opt/sfs-pristine/$b && echo "same $b" || echo "DIFF $b"; done' | sort | uniq -c | sort -rn | head -40
} >> $LOG/provenance.log 2>&1

# ---------- cold build of the patched copy ----------
$APT exec --bind $SRC:/src --bind $WORK:/panel $SIF bash -c 'cd /panel/build && cmake /src -DCMAKE_BUILD_TYPE=Release > /panel/logs/cmake.log 2>&1 && make -j8 > /panel/logs/make.log 2>&1'
echo "--- cold build rc=$?"
md5sum $WORK/build/Hierarchy-Clear | tee $LOG/md5_clear.txt

# ---------- stage ----------
$PY $INS/stage67_inputs.py --lanes $LANES --dataset $DS --pota $POTA --out $TREES > $LOG/stage.log 2>&1
echo "stage rc=$?"
cp -f $INS/axes68/Juglet_Piece_?_Axis.xyz $TREES/juglet/Axes/
md5sum $TREES/juglet/Axes/*.xyz > $LOG/axes.log

printf 'arm\tfloor\ttree\texit\twall_s\n' > $LOG/panel.tsv
runarm () {
  ARM=$1; FLOOR=$2; INC=$3; TREE=$4; NP=$5; EXTRA=$6
  T0=$SECONDS
  echo "##### LAUNCH $ARM floor=$FLOOR tree=$TREE"
  $APT exec --writable-tmpfs \
     --bind $MAIN:/workspace --bind $WORK:/panel --bind $SRC:/src --bind $OUT:/out --bind $TREE:/Dataset/SfS_pp \
     $SIF bash /panel/arm68g.sh $ARM $FLOOR $INC $NP $EXTRA /panel/shim/P.cpp >> $LOG/panel.log 2>&1
  RC=$?
  printf '%s\t%s\t%s\t%s\t%s\n' "$ARM" "$FLOOR" "$TREE" "$RC" "$((SECONDS - T0))" >> $LOG/panel.tsv
  echo "##### $ARM exit=$RC"
}
runarm GJ50  50 /panel/inc1 $TREES/juglet 9 -DJUGLET_ORIG
runarm GPA50 50 /panel/inc2 $TREES/pota   8 NONE

cp $WORK/logs/* $LOG/ 2>/dev/null
md5sum $WORK/build/Hierarchy-* | tee $LOG/md5_binaries.txt
cat $LOG/panel.tsv
for A in GJ50 GPA50; do
  echo "[$A]"; grep -nE "SFS-NO-CANDIDATES|Total number|Segmentation|core dumped|Sherd accuracy" $LOG/binary_$A.log | head
  cat "$OUT/$A/1. Acc.txt" 2>/dev/null
done
echo "=== t68g job finished $(date -u +%FT%TZ)"
