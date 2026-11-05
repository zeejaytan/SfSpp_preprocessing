#!/bin/bash
#SBATCH --job-name=t308c-jug
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=03:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 308 Stage C -- Juglet floor sweep.  Floor in {5,10,15,20,30} x
# {authors' Dataset axes (O), our paper axes (N)} x 2 repeats, NP 9,
# JUGLET_ORIG block, k=5/b=3 shim.  Both axis sets run against the SAME t66
# arm-U jug lanes, so the only difference inside a floor cell is the axis file.
# score58 = the binary-faithful count + per-piece pose error + own-place chamfer;
# jug308_c2.py names the failure mechanism per piece at each floor.
set -uo pipefail

RUN=$SLURM_SUBMIT_DIR
JAXO=__JAXO__
JAXN=__JAXN__
FLOORS="__FLOORS__"
REPS=__REPS__
BLOCK=/data/gpfs/projects/punim2657/SfSpp/runs/20261101-1913_d8f716f_t58-floor-density-panel/work/juglet_orig_block.inc
BLOCK_MD5=401195eae5a41579563fc237a9843298
JUGLANES=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom
DS=/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
MAIN=/data/gpfs/projects/punim2657/sfs_main
SIF=$MAIN/sfs_pristine_assembly.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
SHIPPED=$MAIN/sfspreproc-docker/hpc/tools/main_pristine_batch.cpp
WORK=$RUN/work
OUT=$RUN/out
SC=$RUN/score
NP=9
JOBID=${SLURM_JOB_ID:-na}

for v in $(compgen -e | grep -E "^(SFS_|POT_NAME$)"); do unset "$v"; done
cd "$RUN" || exit 1
mkdir -p "$WORK/inc_src/class" "$WORK/shim" "$OUT" "$SC" logs

echo "[JOB] runid=$(basename "$RUN") job=$JOBID juglet floors=$FLOORS reps=$REPS np=$NP"
echo "[JOB] axes O(authors)=$JAXO  N(ours)=$JAXN"
{ echo "commit $(cat work/code_commit.txt 2>/dev/null || echo na)"; md5sum "$WORK"/*.py "$WORK"/arm67.sh 2>/dev/null; } > logs/code.md5

fail() { local rc=$1; shift
  { echo "jobid=$JOBID"; echo "rc=$rc"; echo "reason: $*"; } > "$RUN/RUN-FAILED.txt"
  echo "[JOB] FATAL rc=$rc $*"; exit "$rc"; }

md5_inputs() { local out=$1 i
  { for i in $(seq 1 9); do
      for f in "$DS/Mesh/Juglet/$(printf "Juglet_Piece_%02d_Mesh.obj" "$i")" "$DS/Axes/Juglet/Juglet_Piece_${i}_Axis.xyz" \
               "$DS/Juglet_GT/Juglet_Piece_${i}_T.txt" "$JUGLANES/Juglet_Piece_${i}.Bl0" \
               "$JUGLANES/Juglet_Piece_${i}.S0" "$JUGLANES/Juglet_Piece_${i}.S1" \
               "$JAXN/Juglet_Piece_${i}_Axis.xyz"; do
        [ -f "$f" ] && printf "%s\t%s\n" "$(md5sum "$f" | cut -d" " -f1)" "$f"
      done
    done
    printf "%s\t%s\n" "$(md5sum "$DS/Juglet_GT/Juglet_simple_graph.txt" | cut -d" " -f1)" "$DS/Juglet_GT/Juglet_simple_graph.txt"
  } | sort -k2 > "$out"; }

md5_inputs "$RUN/logs/inputs_before.md5"
{ echo "jobid $JOBID"; date -u +%FT%TZ; echo "--- SIF"; md5sum "$SIF"
  echo "--- shipped"; md5sum "$SHIPPED"; echo "--- block"; md5sum "$BLOCK"
  echo "--- lanes"; md5sum "$JUGLANES"/*.Bl0 | head -40
  echo "--- axes O"; md5sum "$JAXO"/*.xyz 2>/dev/null | head -20
  echo "--- axes N"; md5sum "$JAXN"/*.xyz 2>/dev/null | head -20; } > "$RUN/logs/provenance.log" 2>&1
cat "$RUN/logs/provenance.log"

[ -f "$SIF" ] || fail 5 "SIF missing"
[ -f "$BLOCK" ] || fail 5 "juglet block inc missing"
[ "$(md5sum "$BLOCK" | cut -d" " -f1)" = "$BLOCK_MD5" ] || fail 5 "juglet block inc md5 mismatch"
[ -d "$JAXO" ] || fail 5 "authors' juglet axes missing: $JAXO"
[ -d "$JAXN" ] || fail 5 "our juglet axes missing: $JAXN"
[ -d "$JUGLANES" ] || fail 5 "t66 jug lanes missing: $JUGLANES"

$PY "$WORK/patch_guard67.py" "$SHIPPED" "$WORK/shim/G.cpp" > logs/guard.log 2>&1
GRC=$?; diff -u "$SHIPPED" "$WORK/shim/G.cpp" > logs/diff_guard.txt 2>&1; md5sum "$SHIPPED" "$WORK/shim/G.cpp" >> logs/guard.log
cat logs/guard.log; [ "$GRC" -eq 0 ] || fail 4 "guard patch failed rc=$GRC"

$APT exec "$SIF" cat /opt/sfs-pristine/class/data_path.h > "$WORK/inc_src/class/data_path.h" 2>>logs/provenance.log
[ -s "$WORK/inc_src/class/data_path.h" ] || fail 6 "could not extract data_path.h from SIF"
mkdir -p "$WORK/inc_jug/class"
$PY "$WORK/mk_inc.py" "$WORK/inc_src/class/data_path.h" "$WORK/inc_jug/class/data_path.h" NONE --append "$BLOCK" > logs/mk_inc.log 2>&1
MRC=$?; cat logs/mk_inc.log; [ "$MRC" -eq 0 ] || fail 6 "mk_inc failed rc=$MRC"
grep -c "^#define POT_" "$WORK/inc_jug/class/data_path.h" > logs/active_pot.log 2>&1 || true; cat logs/active_pot.log

$PY "$WORK/stage67_inputs.py" --lanes "$JUGLANES" --dataset "$DS" --pota "$CORP" --out "$WORK/trees" > logs/stage.log 2>&1
SRC=$?; tail -12 logs/stage.log; [ "$SRC" -eq 0 ] || fail 7 "stage67_inputs failed rc=$SRC"

# the N tree: identical except the Axes files are ours
rm -rf "$WORK/trees/juglet_N"; cp -a "$WORK/trees/juglet" "$WORK/trees/juglet_N" || fail 7 "copy for juglet_N failed"
for i in $(seq 1 9); do
  if [ -s "$JAXN/Juglet_Piece_${i}_Axis.xyz" ]; then
    cp "$JAXN/Juglet_Piece_${i}_Axis.xyz" "$WORK/trees/juglet_N/Axes/Juglet_Piece_${i}_Axis.xyz"
  else
    echo "[JOB] WARN no ours-axis for piece $i -> N leaves it off"
    : > "$WORK/trees/juglet_N/Axes/Juglet_Piece_${i}_Axis.xyz"
  fi
done
( cd "$WORK/trees" && for f in juglet juglet_N; do echo "== $f"; md5sum "$f"/Axes/*.xyz; done ) > logs/trees.md5 2>&1
cat logs/trees.md5
diff -rq "$WORK/trees/juglet" "$WORK/trees/juglet_N" > logs/diff_O_vs_N.txt || true
echo "[JOB] O-vs-N staged trees differ on $(grep -c . logs/diff_O_vs_N.txt) entries, all under Axes/: $(grep -c "/Axes/" logs/diff_O_vs_N.txt)"

printf "arm\tfloor\tinc\ttree\tnp\texit\twall_s\n" > logs/panel.tsv
runarm() { local LABEL=$1 TREE=$2 FLOOR=$3 T0 RC DT
  T0=$SECONDS
  $APT exec --writable-tmpfs \
     --bind "$MAIN":/workspace --bind "$WORK":/panel --bind "$OUT":/out --bind "$TREE":/Dataset/SfS_pp \
     "$SIF" bash /panel/arm67.sh "$LABEL" "$FLOOR" /panel/inc_jug "$NP" -DJUGLET_ORIG \
     > "logs/arm_${LABEL}.log" 2>&1
  RC=$?; DT=$((SECONDS - T0))
  cat "logs/arm_${LABEL}.log" >> logs/panel.log
  grep -E "^(Total number|Node Sequence|End condition)" "logs/arm_${LABEL}.log" > "$SC/${LABEL}.panel.txt" || true
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" "$LABEL" "$FLOOR" /panel/inc_jug "$TREE" "$NP" "$RC" "$DT" >> logs/panel.tsv
  echo "[JOB] $LABEL floor=$FLOOR exit=$RC wall=${DT}s"; }

for F in $FLOORS; do
  for r in $(seq 1 "$REPS"); do
    runarm "F${F}O_r${r}" "$WORK/trees/juglet" "$F"
    runarm "F${F}N_r${r}" "$WORK/trees/juglet_N" "$F"
  done
done
cat logs/panel.tsv

printf "label\ttime_s\tsherd\tedge\n" > "$SC/acc.tsv"
LABELS=""
for F in $FLOORS; do for r in $(seq 1 "$REPS"); do LABELS="$LABELS F${F}O_r${r} F${F}N_r${r}"; done; done
for LABEL in $LABELS; do
  [ -d "$OUT/$LABEL" ] || { echo "[JOB] no Result for $LABEL"; continue; }
  $PY "$WORK/acc305.py" "$OUT/$LABEL" "$LABEL" "$SC/acc.tsv" >> logs/acc.log 2>&1 || true
  $PY "$WORK/score58.py" --result "$OUT/$LABEL" --gt "$DS/Juglet_GT" \
      --mesh "$WORK/trees/juglet/Mesh" --lanes "$WORK/trees/juglet/Breaklines" \
      --out "$SC/$LABEL.json" --label "$LABEL" > logs/score_$LABEL.log 2>&1
  echo "[JOB] scored $LABEL rc=$?"
done

echo "=== binary (1. Acc.txt) ==="; cat "$SC/acc.tsv"
echo "=== score58 summary ==="
for f in "$SC"/*.json; do
  [ -f "$f" ] || continue
  $PY -c "import json,sys; o=json.load(open(sys.argv[1])); c=o.get('countresult',{}); print(o['label'],'sherd=%s/9'%c.get('k_sherd'),'pairs=%s/36'%c.get('k_directed_pass'),'seated=%s'%o.get('seated_count'),'rightway=%s'%o.get('right_way_count'),'T=%s'%len(o.get('pieces_with_T',[])))" "$f"
done

echo "=== C2 mechanism per piece, every cell ==="
for LABEL in $LABELS; do
  [ -f "$SC/$LABEL.json" ] || continue
  F=$(echo "$LABEL" | sed 's/^F0*//; s/[ON]_r[0-9]*$//')
  $PY "$WORK/jug308_c2.py" --result "$OUT/$LABEL" --gt "$DS/Juglet_GT" \
      --lanes "$WORK/trees/juglet/Breaklines" --floor "$F" --json "$SC/$LABEL.json" \
      --out "$SC/$LABEL.c2.tsv" --label "$LABEL" >> logs/c2.log 2>&1
done
cat logs/c2.log

md5_inputs "$RUN/logs/inputs_after.md5"
diff "$RUN/logs/inputs_before.md5" "$RUN/logs/inputs_after.md5" > logs/inputs.diff || true
if [ -s logs/inputs.diff ]; then echo "[JOB] WARN inputs changed"; cat logs/inputs.diff; else echo "[JOB] inputs unchanged"; fi
md5sum "$WORK/build/Hierarchy-"* > logs/binaries.md5 2>/dev/null || true; cat logs/binaries.md5
{ echo "jobid=$JOBID"; echo "utc $(date -u +%Y-%m-%dT%H:%M:%SZ)"; echo "axes O=$JAXO"; echo "axes N=$JAXN"; } > "$RUN/run-meta.txt"
echo "[JOB] complete at $(date -u +%FT%TZ)"