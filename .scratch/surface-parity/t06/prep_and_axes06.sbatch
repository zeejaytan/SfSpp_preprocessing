#!/bin/bash
#SBATCH --job-name=t06-prep
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=logs/slurm-prep-%j.out
#SBATCH --error=logs/slurm-prep-%j.err
# Ticket 06 preparation, on a compute node:
#   1. the four 31-file axis packs -- AUTHOR and OWN_NOV5 copied byte for byte from
#      the Ticket 19 run and pinned, OWN_NOV5_DEDUP extracted from the Nov 5 walls
#      after exact-duplicate removal, OWN_MAIN_T09 extracted from Pot E walls
#      regenerated at pinned commit e91cf791;
#   2. the two e91cf791 binaries built inside $CANON/pcl_191_nurbs.sif;
#   3. wall records (186 rows), axis records (124 rows), fixtures, sources.
# The recipe is the archived t305-lane-e2 one: run_cell66.sh from the pinned commit,
# stage305.sh copied read-only from that run, shipped Pot A mesh defaults, SFS_DEDUPE
# unset, and a corpus md5 before/after proving no corpus input moved.
set -uo pipefail

MAIN=/data/gpfs/projects/punim2657/sfs_main
BASE=/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9
SHIP=${BASE}_t03-ship
T03E=${BASE}_t03-potE
T19=/data/gpfs/projects/punim2657/SfSpp/runs/20261124-0443_21446b8_t19-decisions
RUN5=/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0445_9c5eec2_t305-lane-e2
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
CORP="$MAIN/original_samples/SfS_pp"
SIF_CANON="$CANON/pcl_191_nurbs.sif"
SIF_ASM="$MAIN/sfs_pristine_assembly.sif"
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
NEW=e91cf791
WANT_SHA=0ba6d10fa6885a67a92a92bb37ec7c138f25f32622368bfcafb5bfae3fa637c9
POT=E
PIECES=$(seq -f "Pot_E_Piece_%02g" 1 31 | tr '\n' ' ')
SHIPPED="SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0 SFS_PAPER_NB=10 SFS_SMOOTHNESS_DEG=3.4 SFS_CURVATURE_THRESH=1.0"
RUN="${SLURM_SUBMIT_DIR:?}"
WORK="$RUN/work/t06"
OUT5="$RUN5/out/geom"
OUTM="$RUN/geom_main"
EV="$RUN/evidence"
P=${SLURM_CPUS_PER_TASK:-8}
JOBID="${SLURM_JOB_ID:-na}"

export SFS_IMPL="$SHIP/work/impl_t03"
export PYTHONPATH="$SFS_IMPL:$SHIP/work:$WORK"
export MPLBACKEND=Agg OMP_NUM_THREADS=$P
unset SFS_DEDUPE
for v in $(compgen -e | grep -E '^(SFS_|POT_NAME$)' || true); do unset "$v"; done
export SFS_IMPL="$SHIP/work/impl_t03"
export PYTHONPATH="$SFS_IMPL:$SHIP/work:$WORK"

cd "$RUN" || exit 1
mkdir -p logs work/t06 pins mount build out score evidence renders \
         axes/AUTHOR axes/OWN_NOV5 axes/OWN_NOV5_DEDUP axes/OWN_MAIN_T09 \
         panel/build panel/logs
for pre in "$SHIP/work/t03_lib.py" "$T03E/trees/E_K3R1/E/MM/Ground Truth" "$CORP/Point/MANIFEST_released.tsv" "$SIF_CANON" "$OUT5/Pot_E_Piece_01.S0" "$T19/work/t19/build/Hierarchy-T19"; do
  [ -e "$pre" ] || { echo "RUN-FAIL 6 :: missing prerequisite $pre"; exit 6; }
done
AX="$WORK/axes06.py"
[ -f "$AX" ] || { echo "RUN-FAIL 6 :: axes06.py not staged at $AX"; exit 6; }

fail() { local rc=$1; shift
  { echo "runid=$RUN"; echo "jobid=$JOBID"; echo "commit=$NEW"; echo "rc=$rc"; echo "reason: $*"; } > "$RUN/RUN-FAILED.txt"
  echo "RUN-FAIL $rc :: $*"; exit "$rc"; }

[ -f "$RUN/logs/jobs_submitted.tsv" ] || printf 'job_id\tstage\tarm\trep\n' > "$RUN/logs/jobs_submitted.tsv"
printf '%s\t%s\t%s\t%s\n' "$JOBID" prep - - >> "$RUN/logs/jobs_submitted.tsv"
echo "[PREP] start $(date -u +%FT%TZ) job=$JOBID host=$(hostname)"

printf 'sherd\tsurface_set\tface\tpoints\tduplicate_xyz\txyz_sha256\tnormals_sha256\tsource_sha256\n' > "$EV/walls.tsv"
printf 'sherd\tarm\tstatus\tk\taxes_sha256\teffective_stride\tdrawn_points\tbest_line_deg\tbest_anchor_mm\trank1_line_deg\trank1_anchor_mm\n' > "$EV/axes.tsv"
printf 'arm\tpiece\tk\tsha\n' > "$RUN/pins/axis_pins.tsv"
printf 'AUTHOR\t27\t2\tf1607e000d563216aa8a3a962162ba3b7cfbddefa760b1a797e0d683e0732f8b\n' >> "$RUN/pins/axis_pins.tsv"
printf 'AUTHOR\t28\t2\t212dcb15ae1291980c67bb3de4b9f01936e26c03a9de428c388a424c8c65ede5\n' >> "$RUN/pins/axis_pins.tsv"
printf 'OWN_NOV5\t27\t3\td4236e9115f49b67872369d31fbd7953bd322513af49cfa9cbf30ce8074a4cc6\n' >> "$RUN/pins/axis_pins.tsv"
printf 'OWN_NOV5\t28\t1\t12de83dc2cb91f525854347cc5cea6c34a11d5a65a3d274b91087b33d73d8acf\n' >> "$RUN/pins/axis_pins.tsv"
printf 'OWN_NOV5_DEDUP\t27\t2\ta3e1694d3e291d85ed5d7b57b302c155f7f19a0218f25ac628c65cc24861a39d\n' >> "$RUN/pins/axis_pins.tsv"
printf 'OWN_NOV5_DEDUP\t28\t2\ta5f49e5621bae8bd7cb74efcb30ab419dcf03099d0fd2e78f6a0b2e9b696aa7d\n' >> "$RUN/pins/axis_pins.tsv"

# ---- run.json and the index row are written once the commit resolves (see below) ----

# ---- pin the assembler in the panel (its own executable.sha256 names the mount path) ----
cp -f "$T19/work/t19/build/Hierarchy-T19" "$RUN/panel/build/Hierarchy-T19" || fail 4 "copy panel exe failed"
chmod +x "$RUN/panel/build/Hierarchy-T19"
PS=$(sha256sum "$RUN/panel/build/Hierarchy-T19" | cut -d' ' -f1)
[ "$PS" = "$WANT_SHA" ] || fail 4 "panel exe sha $PS != $WANT_SHA"
printf '%s  %s\n' "$WANT_SHA" "/panel/build/Hierarchy-T19" > "$RUN/panel/logs/executable.sha256"
printf '%s\n' "$WANT_SHA" > "$RUN/logs/exe.sha"
echo "[PREP] panel exe pinned $PS"

# ---- corpus inputs, md5 before and after (the recipe's own gate) ----
mesh_of() { local stem=$1
  if [ -f "$CORP/Mesh/${stem}_Mesh_DS.obj" ]; then echo "$CORP/Mesh/${stem}_Mesh_DS.obj"; else echo "$CORP/Mesh/${stem}_Mesh.obj"; fi; }
md5_inputs() { local out=$1 p
  { for p in $PIECES; do
      for f in "$CORP/Point/Pot_$POT/${p}_Point.pcd" "$(mesh_of "$p")" \
               "$CORP/Axes/${p}_Axis.xyz" "$CORP/Breaklines/${p}_Breakline_0.pcd" \
               "$CORP/Breaklines/${p}_Breakline_1.pcd" "$CORP/Surfaces/${p}_Surface_0.xyz" \
               "$CORP/Surfaces/${p}_Surface_1.xyz"; do
        [ -f "$f" ] && printf "%s\t%s\n" "$(md5sum "$f" | cut -d' ' -f1)" "$f"
      done
    done
  } | sort -k2 > "$out"; }
md5_inputs "$RUN/logs/corpus_inputs_before.md5"
echo "[PREP] corpus inputs before: $(wc -l < "$RUN/logs/corpus_inputs_before.md5") files"

# ---- pinned commit ----
fetch_ok=0
for i in 1 2 3 4 5; do
  if git -C "$CANON" fetch --no-tags origin "+refs/heads/*:refs/remotes/origin/*" >> "$RUN/logs/fetch.log" 2>&1; then fetch_ok=1; break; fi
  sleep $((10 * i))
done
[ "$fetch_ok" -eq 1 ] || fail 2 "git fetch failed"
git -C "$CANON" rev-parse --verify --quiet "$NEW^{commit}" > /dev/null || fail 2 "commit $NEW not in $CANON"
NEW_FULL=$(git -C "$CANON" rev-parse "$NEW")
echo "[PREP] commit $NEW = $NEW_FULL"
cat > "$RUN/run.json" <<JSON
{
  "runid": "$(basename "$RUN")",
  "jobid": "$JOBID",
  "ticket": "surface-parity/06-test-dedup-and-t09-surfaces-in-pot-e-assembly",
  "commit": "17cdab3",
  "scripts_commit": "uncommitted ticket worktree copies, sha256 in evidence/sources.tsv",
  "tag": "t06-dedup-t09",
  "arms": ["AUTHOR", "OWN_NOV5", "OWN_NOV5_DEDUP", "OWN_MAIN_T09"],
  "repeats": [1, 2],
  "pieces": 31,
  "joins": 62,
  "nov5_walls": "$OUT5",
  "regenerated_walls": "$OUTM/geom",
  "preprocessing_commit": "$NEW_FULL",
  "mesh_env": "$SHIPPED",
  "sfs_dedupe": "unset",
  "assembler": "$T19/work/t19/build/Hierarchy-T19",
  "assembler_want_sha": "$WANT_SHA",
  "utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
JSON
IX=/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv
if [ -f "$IX" ] && ! grep -qF "$(basename "$RUN")" "$IX"; then
  printf '%s\t%s\t%s\t%s\t\t\n' "$(basename "$RUN")" "$JOBID" 17cdab3 t06-dedup-t09 >> "$IX"
fi

# ---- byte-for-byte axis packs and their pins ----
cp -a "$T19/axes/AUTHOR/." "$RUN/axes/AUTHOR/" || fail 3 "copy AUTHOR pack"
cp -a "$T19/axes/OWN/." "$RUN/axes/OWN_NOV5/" || fail 3 "copy OWN pack"
for A in AUTHOR OWN_NOV5; do
  N=$(ls "$RUN/axes/$A" | wc -l); [ "$N" -eq 31 ] || fail 3 "pack $A has $N files, want 31"
  for pid in 27 28; do
    F=$(printf "%s/Pot_E_Piece_%02d_Axis.xyz" "$RUN/axes/$A" "$pid")
    K=$(grep -c . "$F"); S=$(sha256sum "$F" | cut -d' ' -f1)
    printf 'PACK %s piece %d k=%d sha=%s\n' "$A" "$pid" "$K" "$S"
  done
done

# ---- build both binaries from the pinned commit ----
ISRC="$RUN/instrsrc"
rm -rf "$ISRC"; mkdir -p "$ISRC"
git -C "$CANON" archive "$NEW_FULL" .scratch/juglet-breaklines/stage55 .scratch/juglet-breaklines/stage66 | tar -x -C "$ISRC" || fail 3 "git archive instruments failed"
INSTR="$ISRC/.scratch/juglet-breaklines/stage66"
STAGER="$RUN/work/stage305.sh"
[ -f "$INSTR/run_cell66.sh" ] || fail 3 "run_cell66.sh missing from $NEW"
[ -f "$STAGER" ] || fail 3 "stage305.sh not staged (scp it from $RUN5/work/stage305.sh)"
md5sum "$INSTR/run_cell66.sh" "$STAGER" > "$RUN/logs/instruments.md5"

FARM="$RUN/work/mesh"; rm -rf "$FARM"; mkdir -p "$FARM"
for p in $PIECES; do ln -sf "$(mesh_of "$p")" "$FARM/${p}_Mesh.obj"; done
echo "[PREP] mesh farm: $(ls "$FARM" | wc -l) links"

BT="$RUN/build/src"
rm -rf "$RUN/build"; mkdir -p "$BT/build"
git -C "$CANON" archive "$NEW_FULL" | tar -x -C "$BT" || fail 3 "git archive $NEW_FULL failed"
[ -d "$BT/alglib" ] || cp -a "$CANON/alglib" "$BT/alglib"
( cd "$BT/build" \
  && "$APT" exec --bind /data:/data "$SIF_CANON" cmake -DCMAKE_BUILD_TYPE=Release .. \
  && "$APT" exec --bind /data:/data "$SIF_CANON" make -j"$P" MeshPreprocessingHeadless EdgeLineExtractionHeadless
) > "$RUN/logs/build.log" 2>&1
if [ -x "$BT/build/MeshPreprocessingHeadless" ] && [ -x "$BT/build/EdgeLineExtractionHeadless" ]; then
  MESH_BIN="$RUN/bin-MeshPreprocessingHeadless"
  EDGE_BIN="$RUN/bin-EdgeLineExtractionHeadless"
  cp -f "$BT/build/MeshPreprocessingHeadless" "$MESH_BIN"
  cp -f "$BT/build/EdgeLineExtractionHeadless" "$EDGE_BIN"
  { echo "commit\t$NEW_FULL"; echo "MeshPreprocessingHeadless\t$(sha256sum "$MESH_BIN" | cut -d' ' -f1)";
    echo "EdgeLineExtractionHeadless\t$(sha256sum "$EDGE_BIN" | cut -d' ' -f1)"; } > "$RUN/binaries.sha256"
  cat "$RUN/binaries.sha256"
else
  grep -n -B2 -A6 -i "error" "$RUN/logs/build.log" | head -60 || true
  fail 5 "build from $NEW_FULL failed"
fi

# ---- the pot's own manifest, built from the frozen manifests (not from disk) ----
MAN="$RUN/pins/MANIFEST_$POT.tsv"
{ printf "piece\tpcd_md5\tkept_points\n"
  awk -F'\t' -v pot="Pot_$POT" 'NR>1 && $1==pot {printf "%s\t%s\t%s\n",$2,$5,$3}' "$CORP/Point/MANIFEST_released.tsv"
  awk -F'\t' -v pot="Pot_$POT" 'NR>1 && index($1,"Pot_" pot "_")==1 {printf "%s\t%s\t%s\n",$1,$5,$4}' "$CORP/Point/MANIFEST_derived.tsv"
} > "$MAN"
echo "[PREP] manifest $MAN: $(($(wc -l < "$MAN") - 1)) rows"

# ---- wall and axis records for the Nov 5 set and the in-memory dedup ----
"$PY" "$AX" walls_axes --set OWN_NOV5 --src "$OUT5" --axes-out "$RUN/axes/OWN_NOV5" \
  --axes-from "$RUN/axes/OWN_NOV5" --walls-tsv "$EV/walls.tsv" --axes-tsv "$EV/axes.tsv" \
  --pins "$RUN/pins/axis_pins.tsv" > "$RUN/logs/axes_OWN_NOV5.log" 2>&1 \
  || fail 7 "OWN_NOV5 walls/axes failed (see logs/axes_OWN_NOV5.log)"
"$PY" "$AX" walls_axes --set AUTHOR --authors --no-walls --axes-out "$RUN/axes/AUTHOR" \
  --axes-from "$RUN/axes/AUTHOR" --walls-tsv "$EV/walls.tsv" --axes-tsv "$EV/axes.tsv" \
  --pins "$RUN/pins/axis_pins.tsv" > "$RUN/logs/axes_AUTHOR.log" 2>&1 \
  || fail 7 "AUTHOR axes rows failed (see logs/axes_AUTHOR.log)"
"$PY" "$AX" walls_axes --set OWN_NOV5_DEDUP --src "$OUT5" --dedupe \
  --axes-out "$RUN/axes/OWN_NOV5_DEDUP" --walls-tsv "$EV/walls.tsv" --axes-tsv "$EV/axes.tsv" \
  --pins "$RUN/pins/axis_pins.tsv" > "$RUN/logs/axes_OWN_NOV5_DEDUP.log" 2>&1 \
  || fail 7 "OWN_NOV5_DEDUP walls/axes failed (see logs/axes_OWN_NOV5_DEDUP.log)"
echo "[PREP] Nov5/dedup records done; walls rows $(($(wc -l < "$EV/walls.tsv") - 1))"

# ---- regenerate Pot E's own walls at e91cf791 (shipped recipe, SFS_DEDUPE unset) ----
unset SFS_DEDUPE
env POT_NAME="Pot_$POT" PIECES="$PIECES" WORNESS="" MESH_ENV="$SHIPPED" OUT="$OUTM" \
    CLOUD_DIR="$CORP/Point/Pot_$POT" MESH_DIR="$FARM" AXIS_DIR="$CORP/Axes" \
    MANIFEST="$MAN" MAN_MD5_COL=pcd_md5 MAN_PTS_COL=kept_points \
    INSTR="$INSTR" PY="$PY" DS="$CANON/Dataset" CORP="$CORP" MESH_BIN="$MESH_BIN" EDGE_BIN="$EDGE_BIN" \
    APT="$APT" SIF="$SIF_CANON" STAGER="$STAGER" RUN="$RUN" JOBID="$JOBID" \
    bash "$INSTR/run_cell66.sh" > "$RUN/logs/cell_Pot_E_main_t09.log" 2>&1
RC=$?
echo "[PREP] regeneration rc=$RC"
[ "$RC" -eq 0 ] || { tail -40 "$RUN/logs/cell_Pot_E_main_t09.log"; fail 8 "regeneration rc=$RC"; }
NS0=$(find "$OUTM/geom" -name '*.S0' -size +0 | wc -l)
NS1=$(find "$OUTM/geom" -name '*.S1' -size +0 | wc -l)
[ "$NS0" -eq 31 ] && [ "$NS1" -eq 31 ] || fail 8 "regenerated walls S0=$NS0 S1=$NS1, want 31/31"
echo "[PREP] regenerated walls S0=$NS0 S1=$NS1"

# ---- [DEDUPE-27] lines: one per surface, mode off ----
grep -h "\[DEDUPE-27\]" "$OUTM"/pieces/*/mesh.log > "$EV/dedupe27.txt" 2>/dev/null || true
ND=$(grep -c "\[DEDUPE-27\]" "$EV/dedupe27.txt")
NOFF=$(grep -c "mode=off" "$EV/dedupe27.txt")
echo "[PREP] [DEDUPE-27] lines=$ND mode=off=$NOFF"
[ "$ND" -eq 62 ] || fail 8 "[DEDUPE-27] lines $ND, want 62"
[ "$NOFF" -eq 62 ] || fail 8 "[DEDUPE-27] mode=off $NOFF, want 62 (SFS_DEDUPE must stay unset)"

# ---- wall and axis records for the regenerated set ----
"$PY" "$AX" walls_axes --set OWN_MAIN_T09 --src "$OUTM/geom" --axes-out "$RUN/axes/OWN_MAIN_T09" \
  --walls-tsv "$EV/walls.tsv" --axes-tsv "$EV/axes.tsv" --pins "$RUN/pins/axis_pins.tsv" \
  > "$RUN/logs/axes_OWN_MAIN_T09.log" 2>&1 \
  || fail 9 "OWN_MAIN_T09 walls/axes failed (see logs/axes_OWN_MAIN_T09.log)"

# ---- gates on the records ----
W=$(($(wc -l < "$EV/walls.tsv") - 1)); A=$(($(wc -l < "$EV/axes.tsv") - 1))
echo "[PREP] walls rows=$W axes rows=$A"
[ "$W" -eq 186 ] || fail 10 "walls.tsv has $W rows, want 186"
[ "$A" -eq 124 ] || fail 10 "axes.tsv has $A rows, want 124"
NZ=$(awk -F'\t' 'NR>1 && ($2=="OWN_NOV5_DEDUP" || $2=="OWN_MAIN_T09") && $5!=0 {n++} END {print n+0}' "$EV/walls.tsv")
Z=$(awk -F'\t' 'NR>1 && ($2=="OWN_NOV5_DEDUP" || $2=="OWN_MAIN_T09") {n++} END {print n+0}' "$EV/walls.tsv")
echo "[PREP] zero-dup gate: $Z walls, $NZ with duplicates left"
[ "$Z" -eq 124 ] || fail 10 "expected 124 dedup/regenerated walls, found $Z"
[ "$NZ" -eq 0 ] || fail 10 "$NZ dedup/regenerated walls still carry duplicate xyz"
[ "$(head -1 "$EV/walls.tsv")" = "$(printf 'sherd\tsurface_set\tface\tpoints\tduplicate_xyz\txyz_sha256\tnormals_sha256\tsource_sha256')" ] || fail 10 "walls.tsv header wrong"
[ "$(head -1 "$EV/axes.tsv")" = "$(printf 'sherd\tarm\tstatus\tk\taxes_sha256\teffective_stride\tdrawn_points\tbest_line_deg\tbest_anchor_mm\trank1_line_deg\trank1_anchor_mm')" ] || fail 10 "axes.tsv header wrong"

# ---- fixtures ----
"$PY" "$AX" fixtures --fixtures "$EV/fixtures.tsv" --posecheck "$WORK/posecheck06.sh" \
  --posecheck-log "$RUN/logs/posecheck_selftest.log" > "$RUN/logs/fixtures.log" 2>&1 \
  || fail 11 "fixtures failed (see logs/fixtures.log)"
tail -6 "$RUN/logs/fixtures.log"

# ---- corpus inputs after ----
md5_inputs "$RUN/logs/corpus_inputs_after.md5"
diff "$RUN/logs/corpus_inputs_before.md5" "$RUN/logs/corpus_inputs_after.md5" > "$RUN/logs/corpus_inputs.diff" || true
[ -s "$RUN/logs/corpus_inputs.diff" ] && { cat "$RUN/logs/corpus_inputs.diff"; fail 12 "corpus inputs changed"; }

# ---- sources.tsv ----
S="$EV/sources.tsv"
row() { printf "%s\t%s\t%s\t%s\t%s\n" "$1" "$2" "$3" "$4" "$5"; }
{
  printf 'kind\tpath\tsha256\tbytes\tdetail\n'
  row commit "$CANON" "$NEW_FULL" 0 "e91cf791 = $NEW_FULL (fetched from origin; git cat-file -e verifies it)"
  row binary "$MESH_BIN" "$(sha256sum "$MESH_BIN" | cut -d' ' -f1)" "$(stat -c %s "$MESH_BIN")" "MeshPreprocessingHeadless built from $NEW_FULL"
  row binary "$EDGE_BIN" "$(sha256sum "$EDGE_BIN" | cut -d' ' -f1)" "$(stat -c %s "$EDGE_BIN")" "EdgeLineExtractionHeadless built from $NEW_FULL"
  row code "$SHIP/work/t03_lib.py" "$(sha256sum "$SHIP/work/t03_lib.py" | cut -d' ' -f1)" "$(stat -c %s "$SHIP/work/t03_lib.py")" "frozen estimator helpers (SHIP)"
  row code "$SHIP/work/t03_extract.py" "$(sha256sum "$SHIP/work/t03_extract.py" | cut -d' ' -f1)" "$(stat -c %s "$SHIP/work/t03_extract.py")" "frozen estimator select/write (SHIP)"
  row code "$T03E/work/score305.py" "$(sha256sum "$T03E/work/score305.py" | cut -d' ' -f1)" "$(stat -c %s "$T03E/work/score305.py")" "pinned scorer, bar 20.05 deg / 50 mm"
  row code "$INSTR/run_cell66.sh" "$(sha256sum "$INSTR/run_cell66.sh" | cut -d' ' -f1)" "$(stat -c %s "$INSTR/run_cell66.sh")" "archived cell recipe from $NEW_FULL"
  row code "$STAGER" "$(sha256sum "$STAGER" | cut -d' ' -f1)" "$(stat -c %s "$STAGER")" "stage305.sh copied from 9c5eec2 t305-lane-e2"
  row exe "$RUN/panel/build/Hierarchy-T19" "$(sha256sum "$RUN/panel/build/Hierarchy-T19" | cut -d' ' -f1)" "$(stat -c %s "$RUN/panel/build/Hierarchy-T19")" "Ticket 19 assembler, WANT_SHA $WANT_SHA"
  row manifest "$MAN" "$(sha256sum "$MAN" | cut -d' ' -f1)" "$(stat -c %s "$MAN")" "Pot E corpus pins from the frozen manifests"
  row corpus "$RUN/logs/corpus_inputs_before.md5" "$(sha256sum "$RUN/logs/corpus_inputs_before.md5" | cut -d' ' -f1)" "$(stat -c %s "$RUN/logs/corpus_inputs_before.md5")" "corpus md5 before: $(wc -l < "$RUN/logs/corpus_inputs_before.md5") files, unchanged after"
  row corpus "$RUN/logs/corpus_inputs.diff" "$(sha256sum "$RUN/logs/corpus_inputs.diff" | cut -d' ' -f1)" "$(stat -c %s "$RUN/logs/corpus_inputs.diff")" "corpus md5 diff: empty"
  row script "$WORK/axes06.py" "$(sha256sum "$WORK/axes06.py" | cut -d' ' -f1)" "$(stat -c %s "$WORK/axes06.py")" "ticket 06 wall/axis records"
  row script "$WORK/prep_and_axes06.sbatch" "$(sha256sum "$WORK/prep_and_axes06.sbatch" | cut -d' ' -f1)" "$(stat -c %s "$WORK/prep_and_axes06.sbatch")" "this job"
  row script "$WORK/cell06.sbatch" "$(sha256sum "$WORK/cell06.sbatch" | cut -d' ' -f1)" "$(stat -c %s "$WORK/cell06.sbatch")" "assembly cell"
  row script "$WORK/posecheck06.sh" "$(sha256sum "$WORK/posecheck06.sh" | cut -d' ' -f1)" "$(stat -c %s "$WORK/posecheck06.sh")" "pose completeness gate"
  row script "$WORK/report06.py" "$(sha256sum "$WORK/report06.py" | cut -d' ' -f1)" "$(stat -c %s "$WORK/report06.py")" "tables and renders"
  row script "$WORK/check06.py" "$(sha256sum "$WORK/check06.py" | cut -d' ' -f1)" "$(stat -c %s "$WORK/check06.py")" "independent check"
} > "$S"
echo "[PREP] sources.tsv rows=$(($(wc -l < "$S") - 1))"
echo "[PREP] complete $(date -u +%FT%TZ)"
exit 0
