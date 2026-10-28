#!/bin/bash
#SBATCH --job-name=t39-ownmode
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=00:40:00
#SBATCH --output=/data/gpfs/projects/punim2657/SfSpp/runs/20261028-1624_ed0fc16_t39-ownmode/logs/slurm-%j.out
#SBATCH --error=/data/gpfs/projects/punim2657/SfSpp/runs/20261028-1624_ed0fc16_t39-ownmode/logs/slurm-%j.err
# ticket 39 -- does SFS_REASSIGN_MODE=own keep the two faces apart?
#
# Ticket 38 measured that the two surfaces the pipeline exports from a silent sherd are real but
# NEST: most of the smaller surface's points also appear in the larger, and the two mean normals
# point the same way.  Own mode changes the admission rule -- a point joins a surface only when
# that surface's own spline is the nearer of the two -- so this job runs the SAME cloud twice per
# piece: arm A the shipped radius mode as the control, arm B own mode.
#
# ONE phase, four cells, two pieces.  Both arms of a piece run back to back inside the same job
# because a control that ran in a different job than its test is not a control.  Before any cell
# runs, each synthetic cloud is checked against ticket 38's own numbers; if the sampler does not
# reproduce them the driver stops and no cell runs.  Arm A is then checked against ticket 38's
# per-surface point counts.
#
# Nothing in the pipeline is modified: it is built from the pushed commit and handed a synthetic
# cloud staged inside this run directory.  Pot A is deliberately not in this job.
set -uo pipefail

RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261028-1624_ed0fc16_t39-ownmode
RUNID=20261028-1624_ed0fc16_t39-ownmode
NEW=ed0fc16328efdb13991e2d9dba843fe7bddb174e
PHASE=1
PHASES_TAG=$(echo "$PHASE" | tr ',' '-')
IXTAG=t39-ownmode
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
DS=$CANON/Dataset
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
RINSTR=$RUN/instruments
OUT=$RUN/out
GEOM=$OUT/geometry
CELLS=$OUT/cells
MREG=$OUT/measure
FIG=$OUT/figures
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
IDX=$RUNS/index.tsv
JOBID=${SLURM_JOB_ID:-na}
P=${SLURM_CPUS_PER_TASK:-8}
unset SFS_COUNT_SCALE SFS_SPACING_POLICY SFS_SPACING_SAMPLES SFS_NORMAL_SOURCE SFS_NORMAL_CARRY \
      SFS_SINGLE_CLUSTER SFS_FLOOR_CEILING SFS_DOWNSAMPLE_TARGET SFS_DUMP_STAGE SFS_DUMP_PIECES \
      SFS_PAPER_THETA SFS_PAPER_KAPPA SFS_PAPER_NB SFS_PAPER_CHAIN SFS_SMOOTHNESS_DEG \
      SFS_CURVATURE_THRESH SFS_REASSIGN_MODE SFS_WINDOW_REPORT 2>/dev/null || true
export CANON CORP DS SIF APT PY OUT GEOM CELLS MREG FIG RUN RUNID NEW PHASE IXTAG RUNS IDX JOBID P

cd "$RUN" || exit 1
mkdir -p "$OUT" "$CELLS" "$MREG" "$FIG" logs

fail() {
  local rc=$1; shift
  {
    echo "runid=$RUNID"
    echo "jobid=$JOBID"
    echo "commit=$NEW"
    echo "tag=$IXTAG"
    echo "rc=$rc"
    echo "reason: $*"
    date -u +"at %Y-%m-%dT%H:%M:%SZ"
  } > "$OUT/RUN-FAILED.txt"
  echo "[JOB] FATAL rc=$rc $* (see out/RUN-FAILED.txt)"
  exit "$rc"
}

echo "[JOB] runid=$RUNID job=$JOBID tag=$IXTAG phase=$PHASE new=$NEW host=$(hostname)"

git -C "$CANON" fetch --no-tags origin "+refs/heads/*:refs/remotes/origin/*" >> logs/fetch.log 2>&1
git -C "$CANON" cat-file -e "${NEW}^{commit}" 2>>logs/fetch.log || fail 2 "commit $NEW not in $CANON"

# the instruments the job executes are the PUSHED COMMIT's bytes, not the run directory's copies
SRC=$RUN/build/src
rm -rf "$SRC"; mkdir -p "$SRC"
git -C "$CANON" archive "$NEW" | tar -x -C "$SRC" || fail 3 "git archive $NEW failed"
INSTR=$SRC/.scratch/juglet-breaklines/stage39/instruments
[ -d "$INSTR" ] || fail 3 "no stage39 instruments in commit $NEW"
( cd "$INSTR" && md5sum *.py *.sh 2>/dev/null ) | sort -k2 > "$OUT/instruments_commit.md5"
( cd "$RINSTR" && md5sum *.py *.sh 2>/dev/null ) | sort -k2 > "$OUT/instruments_rundir.md5"
if ! diff -q "$OUT/instruments_commit.md5" "$OUT/instruments_rundir.md5" > /dev/null; then
  diff "$OUT/instruments_rundir.md5" "$OUT/instruments_commit.md5" || true
  fail 4 "instruments in the run directory differ from commit $NEW"
fi
echo "[JOB] instruments match commit $NEW ($(wc -l < "$OUT/instruments_commit.md5") files)"
STAGER=$INSTR/stage_synth_p38.sh
export INSTR STAGER

corpus_tree() {
  local out=$1
  {
    find "$CORP" -type f -printf "%p\t%s\t%T@\n" | sort
    find "$DS" -type f -printf "%p\t%s\t%T@\n" | sort
    if [ -d /opt/sfs-pristine ]; then
      echo "opt-sfs-pristine PRESENT $(ls -R /opt/sfs-pristine | md5sum | cut -d' ' -f1)"
    else
      echo "opt-sfs-pristine ABSENT"
    fi
  } > "$out"
}
pristine_record() {
  local out=$1
  {
    echo "# /opt/sfs-pristine, recorded from the compute node"
    if [ -d /opt/sfs-pristine ]; then
      echo "status PRESENT"; ls -la /opt/sfs-pristine
    else
      echo "status ABSENT"
      ls -d /opt/sfs-pristine 2>&1 || true
      stat /opt/sfs-pristine 2>&1 || true
    fi
  } > "$out"
}
md5_corpus() {
  local out=$1 f
  {
    for f in "$DS"/Point/Juglet/*.pcd "$DS"/Mesh/Juglet/*.obj "$DS"/Axes/Juglet/*.xyz \
             "$CORP"/Point/Pot_A/*.pcd "$CORP"/Mesh/Pot_A_Piece_*.obj "$CORP"/Axes/*.xyz; do
      [ -f "$f" ] && printf "%s\t%s\n" "$(md5sum "$f" | cut -d' ' -f1)" "$f"
    done
  } | sort -k2 > "$out"
}

corpus_tree "$OUT/corpus_before.tsv"
pristine_record "$OUT/pristine.txt"
md5_corpus "$OUT/inputs_before.md5"
{
  echo "host $(hostname)"
  echo "utc $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "commit $NEW"
  "$PY" -c "import numpy, scipy, sys; print('python', sys.version.split()[0]); print('numpy', numpy.__version__); print('scipy', scipy.__version__)"
  "$APT" --version 2>&1 | head -2
  nproc
} > "$OUT/versions.txt" 2>&1

build_arm() {
  local name=$1 sha=$2 rc
  echo "[BUILD] $name from $sha"
  mkdir -p "build/$name/src/build"
  git -C "$CANON" archive "$sha" | tar -x -C "build/$name/src" || { echo "[BUILD] archive FAILED"; return 1; }
  ( cd "build/$name/src/build" \
    && "$APT" exec --bind /data:/data "$SIF" cmake -DCMAKE_BUILD_TYPE=Release .. \
    && "$APT" exec --bind /data:/data "$SIF" make -j"$P" MeshPreprocessingHeadless \
  ) > "logs/build-$name.log" 2>&1
  rc=$?
  if [ "$rc" -eq 0 ] && [ -x "build/$name/src/build/MeshPreprocessingHeadless" ]; then
    cp -f "build/$name/src/build/MeshPreprocessingHeadless" "$OUT/bin-$name"
    echo "[BUILD] $name ok $(stat -c %s "$OUT/bin-$name") bytes md5=$(md5sum "$OUT/bin-$name" | cut -d' ' -f1)"
    return 0
  fi
  return 1
}

geom_record() {
  local out=$1
  {
    find "$OUT" -type f -printf "%p\t%s\n" 2>/dev/null | awk -F'\t' '
      { n=split($1,a,"."); ext=(n>1?a[n]:"none");
        if (ext !~ /^(pcd|ply|obj|xyz|stl|off)$/) next;
        f[ext]++; b[ext]+=$2; tf++; tb+=$2 }
      END { for (e in f) printf "%s\t%d\t%d\n", e, f[e], b[e];
            printf "TOTAL\t%d\t%d\n", tf, tb }'
  } | sort > "$out"
  cat "$out"
}
geom_delete() {
  local before after
  before=$(find "$OUT" -type f \( -name '*.pcd' -o -name '*.ply' -o -name '*.obj' -o -name '*.xyz' \) | wc -l)
  find "$OUT" -type f \( -name '*.pcd' -o -name '*.ply' -o -name '*.obj' -o -name '*.xyz' \) -print0 \
    | xargs -0 -r rm -f
  rm -rf "$GEOM" "$OUT"/cells-pipeline/stage_* 2>/dev/null || true
  after=$(find "$OUT" -type f \( -name '*.pcd' -o -name '*.ply' -o -name '*.obj' -o -name '*.xyz' \) | wc -l)
  {
    echo "# geometry deleted by $RUNID phase $PHASE, $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "geometry_files_before $before"
    echo "geometry_files_after $after"
    echo "# kept: tsv json log py sh txt png (tables, numbers, sources, figures)"
  } > "$OUT/GEOMETRY_DELETED_phase$PHASES_TAG.txt"
  cat "$OUT/GEOMETRY_DELETED_phase$PHASES_TAG.txt"
}

RC_ANY=0
for PH in $(echo "$PHASE" | tr ',' ' '); do
  echo "[JOB] ---- phase $PH ----"
  case "$PH" in
    1)
      build_arm new "$NEW" || fail 5 "binary build failed (see logs/build-new.log)"
      BIN=$OUT/bin-new; export BIN
      bash "$INSTR/run_cell39.sh" > "$OUT/phase1.log" 2>&1; rc=$?
      ;;
    *)
      fail 6 "unknown phase $PH"
      ;;
  esac
  tail -60 "$OUT/phase$PH.log" 2>/dev/null || true
  if [ "$rc" -ne 0 ]; then
    echo "[JOB] WARN phase $PH driver failed rc=$rc (see out/phase$PH.log); continuing"
    printf "%s\t%s\n" "$PH" "$rc" >> "$OUT/phase_failures.tsv"
    RC_ANY=$rc
  fi
done

# The closing bookkeeping runs once, and also on a termination signal: if Slurm ends this job at the
# wall clock, the corpus is still proved unchanged, the geometry is still counted, deleted and the
# index row still appended, so a timeout cannot leave half a record behind.  Run 6 on ticket 38
# taught that this is a second line of defence and not the first: bash defers a TERM trap until the
# foreground child returns and Slurm's kill wait is shorter than that, so the cells must finish
# well inside --time on their own.
FINISHED=0
finish() {
  [ "$FINISHED" -eq 1 ] && return 0
  FINISHED=1
  corpus_tree "$OUT/corpus_after.tsv"
  md5_corpus "$OUT/inputs_after.md5"
  diff "$OUT/corpus_before.tsv" "$OUT/corpus_after.tsv" > "$OUT/corpus.diff" || true
  diff "$OUT/inputs_before.md5" "$OUT/inputs_after.md5" > "$OUT/inputs.diff" || true
  if [ -s "$OUT/corpus.diff" ] || [ -s "$OUT/inputs.diff" ]; then
    echo "[JOB] WARN the corpus or the frozen inputs changed during this job"
    cat "$OUT/corpus.diff" "$OUT/inputs.diff"
  else
    echo "[JOB] corpus and frozen inputs unchanged"
  fi

  geom_record "$OUT/geometry_counts_phase$PHASES_TAG.tsv"
  geom_delete

  {
    echo "runid=$RUNID"
    echo "jobid=$JOBID"
    echo "commit=$NEW"
    echo "tag=$IXTAG"
    echo "phase=$PHASE"
    echo "host=$(hostname)"
    echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "phase_rc=${rc:-na}"
    echo "phase_failures=$(cat "$OUT/phase_failures.tsv" 2>/dev/null | tr '\n' ' ')"
  } > "$OUT/run-meta_phase$PHASES_TAG.txt"

  printf "%s\t%s\t%s\t%s\t\t\n" "$RUNID" "$JOBID" "$NEW" "$IXTAG" >> "$IDX"
  echo "[JOB] index row appended (verdict and human_note left empty)"
}
trap 'echo "[JOB] signal caught: closing the record before exiting"; finish; exit 143' TERM INT

finish
if [ "$RC_ANY" -ne 0 ]; then
  echo "[JOB] FAILED: one or more phases returned non-zero:"
  cat "$OUT/phase_failures.tsv"
  exit "$RC_ANY"
fi
echo "[JOB] phase $PHASE complete rc=0"
