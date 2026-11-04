#!/bin/bash
#SBATCH --job-name=t305-axes
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 305 Stage 0 / Stage 2 / Stage 4 axes -- the SHIPPED chain, no env overrides.
# The code is pinned by commit: work/code is 'git archive <NEW> sfs_axes' from the canonical
# checkout, and PYTHONPATH points at it (not at the checkout's working tree).
#
#   MODE=stage0 : Pot A, read_surfaces truncate=TRUE  (shipped default) seeds 0,1,2
#                 Pot A, read_surfaces truncate=FALSE (comparator)      seeds 0,1,2
#                 Juglet, our own t66 S0/S1 walls, truncate=TRUE         seeds 0,1,2
#   MODE=corpus : all pots A..J, truncate=TRUE, ticket seed policy (3 seeds for every
#                 Pot A piece and every piece under 5,000 surface points, 1 elsewhere)
#
# Submit: sbatch --export=ALL,NEW=<sha>,RUNID=<id>,MODE=stage0|corpus submit.sbatch
set -uo pipefail

: "${NEW:?}" "${RUNID:?}" "${MODE:?}"
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
RUN=$RUNS/$RUNID
IXTAG=t305-axes-$MODE
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
JUGG=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
JOBID=${SLURM_JOB_ID:-na}
P=${SLURM_CPUS_PER_TASK:-16}

export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
for v in $(compgen -e | grep -E '^(SFS_|POT_NAME$)'); do unset "$v"; done
cd "$RUN" || exit 1
mkdir -p logs work out

echo "[JOB] runid=$RUNID job=$JOBID mode=$MODE commit=$NEW host=$(hostname) at $(date -u +%FT%TZ)"
echo "[JOB] env SFS_* present: $(compgen -e | grep -c '^SFS_') (expect 0)"

md5_corpus() { local out=$1
  { md5sum "$CORP"/Surfaces/*.xyz "$CORP"/Axes/*.xyz; } | sort -k2 > "$out"; }
md5_corpus "$RUN/logs/corpus_md5_before.log"

fetch_ok=0
for i in 1 2 3 4 5; do
  if git -C "$CANON" fetch --no-tags origin "+refs/heads/*:refs/remotes/origin/*" >> "$RUN/logs/fetch.log" 2>&1; then fetch_ok=1; break; fi
  sleep $((10 * i))
done
[ "$fetch_ok" -eq 1 ] || { echo "[JOB] FATAL fetch"; exit 2; }
git -C "$CANON" rev-parse --verify --quiet "$NEW^{commit}" >/dev/null 2>&1 || { echo "[JOB] FATAL commit $NEW absent"; exit 2; }
CODE=$RUN/work/code
rm -rf "$CODE"; mkdir -p "$CODE"
git -C "$CANON" archive "$NEW" sfs_axes | tar -x -C "$CODE" || { echo "[JOB] FATAL archive sfs_axes"; exit 3; }
{ echo "commit $NEW"; md5sum "$CODE"/sfs_axes/*.py; } > "$RUN/logs/code.md5"
cat "$RUN/logs/code.md5"
export PYTHONPATH="$CODE"

if [ "$MODE" = stage0 ]; then
  $PY "$RUN/work/axes305.py" --surfaces "$CORP/Surfaces" --out "$RUN/out/a305" \
      --pot A --seeds 3 --truncate 1 --jobs "$P" --write-seeds 1 > "$RUN/logs/axes_A_trunc.log" 2>&1
  echo "[JOB] Pot A truncate=1 rc=$?"
  $PY "$RUN/work/axes305.py" --surfaces "$CORP/Surfaces" --out "$RUN/out/notrunc" \
      --pot A --seeds 3 --truncate 0 --jobs "$P" --write-seeds 1 > "$RUN/logs/axes_A_notrunc.log" 2>&1
  echo "[JOB] Pot A truncate=0 rc=$?"
  # Juglet: our own t66 walls, renamed into the loader's Pot_JUGLET_Piece_0N convention
  AD=$RUN/work/jugsurf
  rm -rf "$AD"; mkdir -p "$AD"
  for n in 1 2 3 4 5 6 7 8 9; do
    nn=$(printf "%02d" "$n")
    ln -sf "$JUGG/Juglet_Piece_${n}.S0" "$AD/Pot_JUGLET_Piece_${nn}_Surface_0.xyz"
    ln -sf "$JUGG/Juglet_Piece_${n}.S1" "$AD/Pot_JUGLET_Piece_${nn}_Surface_1.xyz"
  done
  md5sum "$JUGG"/Juglet_Piece_?.S0 "$JUGG"/Juglet_Piece_?.S1 > "$RUN/logs/jug_walls.md5"
  $PY "$RUN/work/axes305.py" --surfaces "$AD" --out "$RUN/out/jug" \
      --pot JUGLET --seeds 3 --truncate 1 --jobs 9 --write-seeds 1 > "$RUN/logs/axes_jug.log" 2>&1
  echo "[JOB] Juglet rc=$?"
  mkdir -p "$RUN/out/jug/axes305_jug"
  for n in 1 2 3 4 5 6 7 8 9; do
    nn=$(printf "%02d" "$n")
    src=$RUN/out/jug/axes305/Pot_JUGLET_Piece_${nn}_Axis.xyz
    dst=$RUN/out/jug/axes305_jug/Juglet_Piece_${n}_Axis.xyz
    if [ -f "$src" ]; then cp -f "$src" "$dst"; else : > "$dst"; fi
    printf "Juglet_Piece_%s\t%s bytes\n" "$n" "$(stat -c %s "$dst")"
  done
  md5sum "$RUN/out/jug/axes305_jug/"*.xyz
else
  $PY "$RUN/work/axes305.py" --surfaces "$CORP/Surfaces" --out "$RUN/out" \
      --pot ALL --seeds 0 --truncate 1 --jobs "$P" > "$RUN/logs/axes_ALL.log" 2>&1
  echo "[JOB] ALL rc=$?"
fi

tail -20 "$RUN/logs"/axes_*.log || true
md5_corpus "$RUN/logs/corpus_md5_after.log"
diff "$RUN/logs/corpus_md5_before.log" "$RUN/logs/corpus_md5_after.log" > "$RUN/logs/corpus_md5.diff" || true
if [ -s "$RUN/logs/corpus_md5.diff" ]; then echo "[JOB] WARN corpus changed"; else echo "[JOB] corpus Surfaces+Axes unchanged"; fi
{ echo "runid=$RUNID"; echo "jobid=$JOBID"; echo "commit=$NEW"; echo "tag=$IXTAG"; echo "mode=$MODE";
  echo "utc $(date -u +%Y-%m-%dT%H:%M:%SZ)"; } > "$RUN/run-meta.txt"
echo "[JOB] complete at $(date -u +%FT%TZ)"
