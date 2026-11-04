#!/bin/bash
#SBATCH --job-name=t305-lane
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 305 Stage 1 -- OUR breakline lanes for ONE pot (B, D, E, F, G, I, J).
# The recipe is t66's submit.sbatch + instrsrc (run_cell66.sh unchanged, from the same
# commit; the stager is work/stage305.sh, a copy whose ONLY change is mesh resolution for
# pots C..J): build the two preprocessing binaries from NEW, then run ONE cell.
# Lane identity: Arm U = SFS_ADMIT_SIGN unset, i.e. the shipped default ON (t66's cell recipe).
# Mesh stage env = the shipped Pot A paper defaults, as in t66's pota cell.
# Corpus read-only: md5 of every corpus input this pot reads, before and after.
# Submit:  sbatch --export=ALL,NEW=<sha>,RUNID=<id>,POT=<X>,PIECES="<piece list>" submit.sbatch
set -uo pipefail

: "${NEW:?}" "${RUNID:?}" "${POT:?}" "${PIECES:?}"
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
RUN=$RUNS/$RUNID
IXTAG=t305-lane
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
JOBID=${SLURM_JOB_ID:-na}
P=${SLURM_CPUS_PER_TASK:-8}
SHIPPED="SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0 SFS_PAPER_NB=10 SFS_SMOOTHNESS_DEG=3.4 SFS_CURVATURE_THRESH=1.0"

for v in $(compgen -e | grep -E '^(SFS_|POT_NAME$)'); do unset "$v"; done
cd "$RUN" || exit 1
mkdir -p logs work pins out

echo "[JOB] runid=$RUNID job=$JOBID tag=$IXTAG commit=$NEW pot=$POT host=$(hostname) at $(date -u +%FT%TZ)"
echo "[JOB] pieces: $PIECES"

fail() { local rc=$1; shift
  { echo "runid=$RUNID"; echo "jobid=$JOBID"; echo "commit=$NEW"; echo "tag=$IXTAG"; echo "rc=$rc"; echo "reason: $*"; } > "$RUN/RUN-FAILED.txt"
  echo "[JOB] FATAL rc=$rc $*"; exit "$rc"; }

mesh_of() { # stem -> corpus mesh path (A,B: _Mesh.obj; C..J: _Mesh_DS.obj)
  local stem=$1
  if [ -f "$CORP/Mesh/${stem}_Mesh_DS.obj" ]; then echo "$CORP/Mesh/${stem}_Mesh_DS.obj"; else echo "$CORP/Mesh/${stem}_Mesh.obj"; fi
}
md5_inputs() {
  local out=$1 p stem
  { for p in $PIECES; do
      stem=$p
      for f in "$CORP/Point/Pot_$POT/${p}_Point.pcd" "$(mesh_of $stem)" \
               "$CORP/Axes/${p}_Axis.xyz" "$CORP/Breaklines/${p}_Breakline_0.pcd" \
               "$CORP/Breaklines/${p}_Breakline_1.pcd" "$CORP/Surfaces/${p}_Surface_0.xyz" \
               "$CORP/Surfaces/${p}_Surface_1.xyz"; do
        [ -f "$f" ] && printf "%s\t%s\n" "$(md5sum "$f" | cut -d" " -f1)" "$f"
      done
    done
  } | sort -k2 > "$out"
}

md5_inputs "$RUN/logs/corpus_inputs_before.md5"

# ---- the pot's own manifest, built from the frozen manifests (not from disk) ----
MAN=$RUN/pins/MANIFEST_$POT.tsv
{ printf "piece\tpcd_md5\tkept_points\n"
  awk -F'\t' -v pot="Pot_$POT" 'NR>1 && $1==pot {printf "%s\t%s\t%s\n",$2,$5,$3}' "$CORP/Point/MANIFEST_released.tsv"
  awk -F'\t' -v pot="Pot_$POT" 'NR>1 && index($1,pot "_")==1 {printf "%s\t%s\t%s\n",$1,$5,$4}' "$CORP/Point/MANIFEST_derived.tsv"
} > "$MAN"
echo "[JOB] manifest $MAN: $(($(wc -l < "$MAN") - 1)) rows for Pot_$POT (released + derived)"
head -3 "$MAN"

mesh_md5() { md5sum "$1" | cut -d" " -f1; }

fetch_ok=0
for i in 1 2 3 4 5; do
  if git -C "$CANON" fetch --no-tags origin "+refs/heads/*:refs/remotes/origin/*" >> "$RUN/logs/fetch.log" 2>&1; then fetch_ok=1; break; fi
  sleep $((10 * i))
done
[ "$fetch_ok" -eq 1 ] || fail 2 "git fetch failed"
git -C "$CANON" rev-parse --verify --quiet "$NEW^{commit}" >/dev/null 2>>"$RUN/logs/fetch.log" || fail 2 "commit $NEW not in $CANON"
echo "[JOB] commit verified: $(git -C "$CANON" rev-parse "$NEW")"

ISRC=$RUN/instrsrc
rm -rf "$ISRC"; mkdir -p "$ISRC"
git -C "$CANON" archive "$NEW" .scratch/juglet-breaklines/stage55 .scratch/juglet-breaklines/stage66 | tar -x -C "$ISRC" || fail 3 "git archive instruments failed"
INSTR=$ISRC/.scratch/juglet-breaklines/stage66
STAGER=$RUN/work/stage305.sh
[ -f "$INSTR/run_cell66.sh" ] || fail 3 "run_cell66.sh missing"
[ -f "$STAGER" ] || fail 3 "stage305.sh missing (scp'd by driver.py)"
md5sum "$INSTR/run_cell66.sh" "$STAGER" > "$RUN/logs/instruments.md5"

# mesh farm: the frozen stager only knows Pot_A's flat corpus path, and the Dataset
# per-pot copy uses the plain _Mesh.obj suffix -- pots C..J ship <stem>_Mesh_DS.obj.
# One symlink per piece under <RUN>/work/mesh gives the gate and the stager the
# <stem>_Mesh.obj name they expect, pointing at the one real corpus mesh.
FARM=$RUN/work/mesh; rm -rf "$FARM"; mkdir -p "$FARM"
for p in $PIECES; do ln -sf "$(mesh_of "$p")" "$FARM/${p}_Mesh.obj"; done
ls -l "$FARM" | head -3; echo "[JOB] mesh farm: $(ls "$FARM" | wc -l) links"

BT=$RUN/build/src
rm -rf "$RUN/build"; mkdir -p "$BT/build"
git -C "$CANON" archive "$NEW" | tar -x -C "$BT" || fail 3 "git archive $NEW failed"
[ -d "$BT/alglib" ] || cp -a "$CANON/alglib" "$BT/alglib"
( cd "$BT/build" \
  && "$APT" exec --bind /data:/data "$SIF" cmake -DCMAKE_BUILD_TYPE=Release .. \
  && "$APT" exec --bind /data:/data "$SIF" make -j"$P" MeshPreprocessingHeadless EdgeLineExtractionHeadless
) > "$RUN/logs/build.log" 2>&1
if [ -x "$BT/build/MeshPreprocessingHeadless" ] && [ -x "$BT/build/EdgeLineExtractionHeadless" ]; then
  MESH_BIN=$RUN/bin-MeshPreprocessingHeadless
  EDGE_BIN=$RUN/bin-EdgeLineExtractionHeadless
  cp -f "$BT/build/MeshPreprocessingHeadless" "$MESH_BIN"
  cp -f "$BT/build/EdgeLineExtractionHeadless" "$EDGE_BIN"
  { echo "commit\t$NEW (unpatched)"; 
    echo "MeshPreprocessingHeadless\t$(mesh_md5 "$MESH_BIN")";
    echo "EdgeLineExtractionHeadless\t$(mesh_md5 "$EDGE_BIN")"; } > "$RUN/binaries.md5"
  cat "$RUN/binaries.md5"
else
  grep -n -B2 -A6 "error" "$RUN/logs/build.log" | head -60 || true
  fail 5 "build failed"
fi

OUT=$RUN/out
env POT_NAME="Pot_$POT" PIECES="$PIECES" WORNESS="" MESH_ENV="$SHIPPED" OUT="$OUT" \
    CLOUD_DIR="$CORP/Point/Pot_$POT" MESH_DIR="$FARM" AXIS_DIR="$CORP/Axes" \
    MANIFEST="$MAN" MAN_MD5_COL=pcd_md5 MAN_PTS_COL=kept_points \
    INSTR="$INSTR" PY="$PY" DS="$CANON/Dataset" CORP="$CORP" MESH_BIN="$MESH_BIN" EDGE_BIN="$EDGE_BIN" \
    APT="$APT" SIF="$SIF" STAGER="$STAGER" RUN="$RUN" JOBID="$JOBID" \
    bash "$INSTR/run_cell66.sh" > "$RUN/logs/cell_Pot_$POT.log" 2>&1
RC=$?
echo "[JOB] cell rc=$RC"
tail -25 "$RUN/logs/cell_Pot_$POT.log" || true

{ echo "gem files:"; ls "$OUT/geom" 2>/dev/null | wc -l
  echo "Bl0 non-empty:"; find "$OUT/geom" -name '*.Bl0' -size +0 2>/dev/null | wc -l
  echo "Bl0 md5:"; md5sum "$OUT"/geom/*.Bl0 2>/dev/null
} > "$RUN/logs/lanes_record.txt"
cat "$RUN/logs/lanes_record.txt"

md5_inputs "$RUN/logs/corpus_inputs_after.md5"
diff "$RUN/logs/corpus_inputs_before.md5" "$RUN/logs/corpus_inputs_after.md5" > "$RUN/logs/corpus_inputs.diff" || true
if [ -s "$RUN/logs/corpus_inputs.diff" ]; then echo "[JOB] WARN corpus changed"; cat "$RUN/logs/corpus_inputs.diff"; else echo "[JOB] corpus inputs unchanged"; fi

{ echo "runid=$RUNID"; echo "jobid=$JOBID"; echo "commit=$NEW"; echo "tag=$IXTAG"; echo "pot=$POT";
  echo "utc $(date -u +%Y-%m-%dT%H:%M:%SZ)"; echo "rc=$RC"; } > "$RUN/run-meta.txt"
echo "[JOB] complete rc=$RC at $(date -u +%FT%TZ)"
exit "$RC"
