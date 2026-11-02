#!/bin/bash
#SBATCH --job-name=t55-brk
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=03:30:00
#SBATCH --output=/data/gpfs/projects/punim2657/SfSpp/runs/20261101-2004_05be12c_t55-worness07-breaklines/logs/slurm-%j.out
#SBATCH --error=/data/gpfs/projects/punim2657/SfSpp/runs/20261101-2004_05be12c_t55-worness07-breaklines/logs/slurm-%j.err
# ticket 55 -- the Juglet chain at WORNESS=0.7 down to breaklines, every edgeline rendered.
# No source change, one job: build BOTH binaries (MeshPreprocessingHeadless,
# EdgeLineExtractionHeadless) from git archive of the PUSHED commit, then all nine Juglet
# pieces through the shipped chain at SFS_WORNESS=0.7 (mesh stage then edge stage) inside
# run_cell55.sh, which first gates the corpus against MANIFEST_JUGLET_CC.tsv (t54 pass 1,
# identical), exports out/geom/<P>.{S0,S1,Bl0,Bl1} (KEPT: the future assembly ticket
# consumes it), deletes every counted stage, and marks a piece FAILED (never dropped) when
# either required marker ('[PAPER-234] classify: face0', '[WORNESS-54] piece=' with theta)
# or any export is missing.  render55.py then draws one PNG per piece (mesh light-grey
# scatter, Bl0/Bl1 in distinct bright colours, two fixed panels so the rim is edge-on in
# one, mm equal-aspect axes).  Nothing is assembled, scored or written into the corpus; the
# index row is appended with verdict/human_note EMPTY (written by the lead only).
#
# Paid-for traps this script is written around (the t54 list): CRLF in any script (grep gate
# in the submitter); unbound variables under set -u; no xargs -d; grep -a on binary
# PCD/PLY; PLY header length varies; every SFS_* unset up front and between pieces.
set -uo pipefail

RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261101-2004_05be12c_t55-worness07-breaklines
RUNID=20261101-2004_05be12c_t55-worness07-breaklines
NEW=05be12c28e252a3b06410b2cf5126ef8afa19064
IXTAG=t55-worness07-breaklines
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
DS=$CANON/Dataset
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
RINSTR=$RUN/instruments
OUT=$RUN/out
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
IDX=$RUNS/index.tsv
JOBID=$SLURM_JOB_ID; [ -n "$JOBID" ] || JOBID=na
P=$SLURM_CPUS_PER_TASK; [ -n "$P" ] || P=8
unset SFS_COUNT_SCALE SFS_SPACING_POLICY SFS_SPACING_SAMPLES SFS_NORMAL_SOURCE SFS_NORMAL_CARRY \
      SFS_SINGLE_CLUSTER SFS_FLOOR_CEILING SFS_DOWNSAMPLE_TARGET SFS_DUMP_STAGE SFS_DUMP_PIECES \
      SFS_PAPER_THETA SFS_PAPER_KAPPA SFS_PAPER_NB SFS_PAPER_CHAIN SFS_SMOOTHNESS_DEG \
      SFS_CURVATURE_THRESH SFS_REASSIGN_MODE SFS_WINDOW_REPORT SFS_MERGE_SCALE SFS_GROWTH_MODE \
      SFS_GROWTH_FORMULA SFS_GROWTH_CAP SFS_GROWTH_WALK SFS_WORNESS SFS_AXIS_FILE SFS_STATUS_FILE POT_NAME 2>/dev/null || true
export CANON CORP DS SIF APT PY OUT RUN RUNID NEW IXTAG RUNS IDX JOBID P

cd "$RUN" || exit 1
mkdir -p "$OUT" logs

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

echo "[JOB] runid=$RUNID job=$JOBID tag=$IXTAG new=$NEW host=$(hostname)"

git -C "$CANON" fetch --no-tags origin "+refs/heads/*:refs/remotes/origin/*" >> logs/fetch.log 2>&1
git -C "$CANON" rev-parse --verify --quiet "$NEW" > /dev/null 2>>logs/fetch.log || fail 2 "commit $NEW not in $CANON"

# the instruments the job executes are the PUSHED COMMIT bytes, not the run directory copies
ISRC=$RUN/instrsrc
rm -rf "$ISRC"; mkdir -p "$ISRC"
git -C "$CANON" archive "$NEW" .scratch/juglet-breaklines/stage55 | tar -x -C "$ISRC" \
  || fail 3 "git archive $NEW failed"
INSTR=$ISRC/.scratch/juglet-breaklines/stage55/instruments
[ -d "$INSTR" ] || fail 3 "no stage55 instruments in commit $NEW"
( cd "$INSTR" && md5sum *.py *.sh *.tsv 2>/dev/null ) | sort -k2 > "$OUT/instruments_commit.md5"
( cd "$RINSTR" && md5sum *.py *.sh *.tsv 2>/dev/null ) | sort -k2 > "$OUT/instruments_rundir.md5"
if ! diff -q "$OUT/instruments_commit.md5" "$OUT/instruments_rundir.md5" > /dev/null; then
  diff "$OUT/instruments_rundir.md5" "$OUT/instruments_commit.md5" || true
  fail 4 "instruments in the run directory differ from commit $NEW"
fi
echo "[JOB] instruments match commit $NEW ($(wc -l < "$OUT/instruments_commit.md5") files)"
STAGER=$INSTR/stage_synth_p40.sh
export INSTR STAGER

md5_corpus() {  # the frozen Juglet inputs only -- this ticket touches no other pot
  local out=$1 f
  {
    for f in "$DS"/Point/Juglet/*.pcd "$DS"/Point/Juglet/MANIFEST_JUGLET_CC.tsv \
             "$DS"/Mesh/Juglet/*.obj "$DS"/Axes/Juglet/*.xyz; do
      [ -f "$f" ] && printf "%s\t%s\n" "$(md5sum "$f" | cut -d" " -f1)" "$f"
    done
  } | sort -k2 > "$out"
}

geom_record() {
  local out=$1
  {
    find "$OUT" -type f -printf "%p\t%s\n" 2>/dev/null | awk -F"\t" '{
      { n=split($1,a,"."); ext=(n>1?a[n]:"none");
        if (ext !~ /^(pcd|ply|obj|xyz|stl|off)$/) next;
        f[ext]++; b[ext]+=$2; tf++; tb+=$2 }
      END { for (e in f) printf "%s\t%d\t%d\n", e, f[e], b[e];
            printf "TOTAL\t%d\t%d\n", tf, tb }'
  } | sort > "$out"
  cat "$out"
}
geom_delete() {
  # ticket 55 KEEPS the out/geom bundle (the future assembly ticket consumes it) and the
  # out/ pngs: every OTHER geometry file under out/ is deleted, leftover stages included,
  # and the delete records itself first -- what is kept is named, not implied.
  local before after kept
  before=$(find "$OUT" -type f \( -name "*.pcd" -o -name "*.ply" -o -name "*.obj" -o -name "*.xyz" \) | wc -l)
  kept=$(find "$OUT/geom" -type f 2>/dev/null | wc -l)
  find "$OUT" -type f \( -name "*.pcd" -o -name "*.ply" -o -name "*.obj" -o -name "*.xyz" \) \
    -not -path "$OUT/geom/*" -print0 | xargs -0 -r rm -f
  rm -rf "$OUT"/stages 2>/dev/null || true
  after=$(find "$OUT" -type f \( -name "*.pcd" -o -name "*.ply" -o -name "*.obj" -o -name "*.xyz" \) | wc -l)
  {
    echo "# geometry deleted by $RUNID, $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "geometry_files_before $before"
    echo "geometry_files_after $after"
    echo "kept_geom_bundle_files $kept"
    echo "# kept: out/geom/* (the assembly-consumable bundle), out/png/*.png; tsv json log py sh txt"
  } > "$OUT/GEOMETRY_DELETED.txt"
  cat "$OUT/GEOMETRY_DELETED.txt"
}

JUG="Juglet_Piece_1 Juglet_Piece_2 Juglet_Piece_3 Juglet_Piece_4 Juglet_Piece_5 Juglet_Piece_6 Juglet_Piece_7 Juglet_Piece_8 Juglet_Piece_9"

md5_corpus "$OUT/inputs_before.md5"
{
  echo "host $(hostname)"
  echo "utc $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "commit $NEW"
  "$PY" -c "import numpy, scipy, sys; print('python', sys.version.split()[0]); print('numpy', numpy.__version__); print('scipy', scipy.__version__)" 2>&1
  "$PY" -c "import matplotlib; print('matplotlib', matplotlib.__version__)" 2>&1
  "$APT" --version 2>&1 | head -2
  nproc
} > "$OUT/versions.txt" 2>&1
cat "$OUT/versions.txt"

# ---- build BOTH binaries from the git archive of the pushed commit (one tree, both targets)
BT=$RUN/build/src
rm -rf "$RUN/build"; mkdir -p "$BT/build"
echo "[BUILD] both binaries from $NEW"
git -C "$CANON" archive "$NEW" | tar -x -C "$BT" || { echo "[BUILD] archive FAILED"; fail 3 "git archive $NEW failed"; }
[ -d "$BT/alglib" ] || cp -a "$CANON/alglib" "$BT/alglib"   # defensive: p298 copied it; the archive normally carries it
( cd "$BT/build" \
  && "$APT" exec --bind /data:/data "$SIF" cmake -DCMAKE_BUILD_TYPE=Release .. \
  && "$APT" exec --bind /data:/data "$SIF" make -j"$P" MeshPreprocessingHeadless EdgeLineExtractionHeadless
) > logs/build.log 2>&1
BRC=$?
if [ "$BRC" -eq 0 ] && [ -x "$BT/build/MeshPreprocessingHeadless" ] && [ -x "$BT/build/EdgeLineExtractionHeadless" ]; then
  MESH_BIN=$OUT/bin-MeshPreprocessingHeadless
  EDGE_BIN=$OUT/bin-EdgeLineExtractionHeadless
  cp -f "$BT/build/MeshPreprocessingHeadless" "$MESH_BIN"
  cp -f "$BT/build/EdgeLineExtractionHeadless" "$EDGE_BIN"
  {
    echo "commit	$NEW"
    echo "MeshPreprocessingHeadless	$(md5sum "$MESH_BIN" | cut -d" " -f1)	$(stat -c %s "$MESH_BIN") bytes"
    echo "EdgeLineExtractionHeadless	$(md5sum "$EDGE_BIN" | cut -d" " -f1)	$(stat -c %s "$EDGE_BIN") bytes"
  } > "$OUT/binaries.md5"
  cat "$OUT/binaries.md5"
else
  tail -40 logs/build.log || true
  fail 5 "binary build failed (see logs/build.log)"
fi
export MESH_BIN EDGE_BIN

# ---- the cells: corpus gate + 9 pieces (mesh stage then edge stage)
export PIECES="$JUG" WORNESS=0.7
echo "[JOB] cells: $(echo $PIECES | wc -w) pieces, SFS_WORNESS=$WORNESS"
bash "$INSTR/run_cell55.sh" > "$OUT/cells55.log" 2>&1
rc=$?
[ -s "$OUT/cells55.log" ] && tail -150 "$OUT/cells55.log"
RC_ANY=$rc
if [ "$rc" -ne 0 ]; then
  echo "[JOB] WARN run_cell55 rc=$rc (see out/cells55.log); the closing record is still written"
fi

# ---- the pictures: one PNG per piece, theta read from the pieces table
mkdir -p "$OUT/png"
printf "piece\ttheta\tpng\tbytes\trc\tnote\n" > "$OUT/render55.tsv"
: > "$OUT/render55.log"
for P in $JUG; do
  TH=na
  [ -f "$OUT/pieces55.tsv" ] && TH=$(awk -F"\t" -v p="$P" '$1==p {print $2}' "$OUT/pieces55.tsv")
  [ -n "$TH" ] || TH=na
  if [ ! -f "$OUT/geom/${P}.Bl0" ] || [ ! -f "$OUT/geom/${P}.Bl1" ]; then
    echo "[JOB] render skip $P: no Bl0/Bl1 bundle in out/geom"
    printf "%s\t%s\t%s\t%s\t%s\t%s\n" "$P" "$TH" - - skip "no Bl0/Bl1 in out/geom" >> "$OUT/render55.tsv"
    continue
  fi
  "$PY" "$INSTR/render55.py" --piece "$P" --mesh "$DS/Mesh/Juglet/${P}_Mesh.obj" \
    --bl0 "$OUT/geom/${P}.Bl0" --bl1 "$OUT/geom/${P}.Bl1" --theta "$TH" \
    --out "$OUT/png/${P}.png" >> "$OUT/render55.log" 2>&1
  RRC=$?
  NOTE=ok
  [ "$RRC" -ne 0 ] && { NOTE="render rc=$RRC (see out/render55.log)"; RC_ANY=$RRC; }
  printf "%s\t%s\t%s\t%s\t%s\t%s\n" "$P" "$TH" "$OUT/png/${P}.png" \
    "$( [ -f "$OUT/png/${P}.png" ] && stat -c %s "$OUT/png/${P}.png" || echo -)" "$RRC" "$NOTE" >> "$OUT/render55.tsv"
done
cat "$OUT/render55.tsv"
NPNG=$(find "$OUT/png" -name "*.png" 2>/dev/null | wc -l)
echo "[JOB] renders: $NPNG png of 9 pieces"

# ---- md5 of every exported file this bundle is judged on (geom bundle + pngs)
: > "$OUT/files.md5"
for f in "$OUT"/geom/* "$OUT"/png/*.png; do
  [ -f "$f" ] && printf "%s\t%s\t%s bytes\n" "$(md5sum "$f" | cut -d" " -f1)" "$f" "$(stat -c %s "$f")" >> "$OUT/files.md5"
done
echo "[JOB] files.md5 rows: $(wc -l < "$OUT/files.md5")"

# The closing bookkeeping runs once, and also on a termination signal: if Slurm ends this job
# at the wall clock, the frozen inputs are still proved unchanged, the geometry is still
# counted, deleted and the index row still appended, so a timeout cannot leave half a record.
FINISHED=0
finish() {
  [ "$FINISHED" -eq 1 ] && return 0
  FINISHED=1
  md5_corpus "$OUT/inputs_after.md5"
  diff "$OUT/inputs_before.md5" "$OUT/inputs_after.md5" > "$OUT/inputs.diff" || true
  if [ -s "$OUT/inputs.diff" ]; then
    echo "[JOB] WARN the frozen inputs changed during this job"
    cat "$OUT/inputs.diff"
  else
    echo "[JOB] frozen inputs unchanged (empty corpus diff)"
  fi

  geom_record "$OUT/geometry_counts.tsv"
  geom_delete

  {
    echo "runid=$RUNID"
    echo "jobid=$JOBID"
    echo "commit=$NEW"
    echo "tag=$IXTAG"
    echo "host=$(hostname)"
    echo "utc $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "cells_rc=$rc"
    echo "png_count=$(find "$OUT/png" -name "*.png" 2>/dev/null | wc -l)"
    echo "geom_bundle=$(ls "$OUT/geom" 2>/dev/null | wc -l) files"
  } > "$OUT/run-meta.txt"

  printf "%s\t%s\t%s\t%s\t\t\n" "$RUNID" "$JOBID" "$NEW" "$IXTAG" >> "$IDX"
  echo "[JOB] index row appended (verdict and human_note left empty)"
}
trap 'echo "[JOB] signal caught: closing the record before exiting"; finish; exit 143' TERM INT

finish
if [ "$RC_ANY" -ne 0 ]; then
  echo "[JOB] FAILED: a driver returned non-zero"
  cat "$OUT"/phase_failures.tsv 2>/dev/null || true
  exit "$RC_ANY"
fi
echo "[JOB] complete rc=0"
