#!/bin/bash
#SBATCH --job-name=t310a-stage
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 310 Stage A -- what separates the lines that seat from the lines that do not.
# Piece A_08 (the piece that seats 8/8 15/15 only when the good axis is written) over
# 24 seeds, with A_01 and A_04 as controls. Per seed: the shipped axfile (run_potsac,
# production call) + the 1000-draw pool, stage-1 refined, and for every written line and
# every 10-deg basin representative the per-wall/per-point statistics Stage A asks for.
# Axes only; no assembly here.
set -uo pipefail
RUN=$SLURM_SUBMIT_DIR
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
JOBID=${SLURM_JOB_ID:-na}
cd "$RUN" || exit 1
mkdir -p logs out

fail() { local rc=$1; shift; { echo "jobid=$JOBID"; echo "rc=$rc"; echo "reason: $*"; } > "$RUN/RUN-FAILED.txt"; echo "[JOB] FATAL rc=$rc $*"; exit "$rc"; }

corpus_md5() {
  { md5sum "$CORP"/Axes/*.xyz
    md5sum "$CORP"/Surfaces/*_Surface_*.xyz
    md5sum "$CORP"/Breaklines/*_Breakline_0.pcd
  } | sort -k2 > "$1"
}

echo "[JOB] jobid=$JOBID start $(date -u +%FT%TZ)"
{ echo "jobid $JOBID"; date -u +%FT%TZ
  echo "--- instruments"; md5sum work/*.py work/sfs_axes/*.py
  echo "--- commit"; cat work/code_commit.txt 2>/dev/null
} > logs/provenance.log 2>&1
corpus_md5 logs/corpus_before.md5
echo "[JOB] corpus paths before: $(wc -l < logs/corpus_before.md5)"

# The labelling reference: the axis that seated in ticket 308 (Piece 08, seeds 1/4/5,
# the three instances agree to 0.19 deg), position-first. Used to LABEL good/wrong for
# the separation table and the prevalence count. Never an input to a rule.
cat > work/good310.xyz <<'EOF'
-108.386571923058 -3.196271060505 235.738430695234 0.902828462984 -0.117983703089 0.413498019623
EOF
echo "[JOB] good ref:"; cat work/good310.xyz

# --- smoke: one seed, one worker. If the instrument is broken, stop here.
$PY work/stage310a.py --out "$RUN/out/smoke" --pot A --pieces 8 --seeds 0:1 --jobs 1 \
    --good "$RUN/work/good310.xyz" > logs/smoke.log 2>&1
SRC=$?
tail -20 logs/smoke.log
echo "[JOB] smoke rc=$SRC"
[ "$SRC" -eq 0 ] || fail 12 "smoke stage310a rc=$SRC"
echo "[JOB] smoke written.tsv rows: $(wc -l < out/smoke/p8/s0/written.tsv)"

# --- Piece 08: 24 seeds (the piece the whole ticket rests on)
$PY work/stage310a.py --out "$RUN/out" --pot A --pieces 8 --seeds 0:24 --jobs 7 \
    --good "$RUN/work/good310.xyz" > logs/stage8.log 2>&1
P8=$?
echo "[JOB] piece 8 rc=$P8  cases=$(ls -d out/p8/s* 2>/dev/null | wc -l)"
tail -6 logs/stage8.log

# --- controls: A_01 and A_04, 16 seeds each
$PY work/stage310a.py --out "$RUN/out" --pot A --pieces 1,4 --seeds 0:16 --jobs 7 \
    --good "$RUN/work/good310.xyz" > logs/stage14.log 2>&1
PC=$?
echo "[JOB] controls rc=$PC  cases=$(ls -d out/p1/s* out/p4/s* 2>/dev/null | wc -l)"
tail -6 logs/stage14.log

corpus_md5 logs/corpus_after.md5
diff logs/corpus_before.md5 logs/corpus_after.md5 > logs/corpus.diff || true
if [ -s logs/corpus.diff ]; then echo "[JOB] WARN corpus changed"; cat logs/corpus.diff; else echo "[JOB] corpus unchanged ($(wc -l < logs/corpus_before.md5) paths)"; fi

[ -f out/summary.tsv ] && { echo "[JOB] out/summary.tsv:"; cat out/summary.tsv; }
echo "[JOB] done $(date -u +%FT%TZ) p8rc=$P8 crc=$PC"
[ "$P8" -eq 0 ] || exit 13
[ "$PC" -eq 0 ] || exit 14
