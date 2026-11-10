#!/bin/bash
#SBATCH --job-name=t328ax
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --mem=48G
#SBATCH --time=00:40:00
#
# Ticket 328, job E: bar 5's byte-identity test. scripts/run_benchmark_172.py is run
# exactly as t322/t323 ran it (their impl dir = working-tree sfs_axes, --cap 6 --seeds 10
# --step 10, 24 jobs) and its output is compared with axes322; the t323 rule (tau 1.2,
# kmax 3) is then applied with t323's own script and that output compared with axes323
# (172 files, 251 lines). This benchmark reads frozen corpus surfaces and the t66 Juglet
# geom and never touches the mesh or edge binaries, so it is insensitive to ticket 328's
# change by construction -- recorded here so the claim is measured, not asserted.
set -uo pipefail
: "${RUNID:?}"
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
RUN=$RUNS/$RUNID
T322=$RUNS/20261110-0415_d628fc0_t322-axes
T323=$RUNS/20261110-0740_d628fc0_t323-axes
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
cd "$RUN" || exit 1
mkdir -p out logs
fail() { echo "[JOB] FATAL $*"; echo "$*" > RUN-FAILED-E.txt; exit 1; }
echo "[JOB] $(basename $RUN) job=${SLURM_JOB_ID:-na} start=$(date -u +%FT%TZ)"
cd "$T322/impl" || fail "no impl dir"
md5sum run_benchmark_172.py sfs_axes/*.py > "$RUN/out/axes328_code.md5"
"$PY" run_benchmark_172.py --out "$RUN/out/axes328" --jobs 24 --cap 6 --seeds 10 --step 10 > "$RUN/logs/axes328.log" 2>&1
echo "[JOB] benchmark rc=$? files=$(ls "$RUN/out/axes328" | wc -l) lines=$(cat "$RUN/out/axes328"/*.xyz | wc -l)"
tail -4 "$RUN/logs/axes328.log"
( cd "$RUN/out/axes328" && md5sum *.xyz ) > "$RUN/out/axes328.md5"
diff -rq "$T322/out/axes322" "$RUN/out/axes328" > "$RUN/out/axes328_vs_axes322.diff" 2>&1
echo "[JOB] vs axes322: diff lines=$(wc -l < "$RUN/out/axes328_vs_axes322.diff") files_same=$([ -s "$RUN/out/axes328_vs_axes322.diff" ] && echo no || echo yes)"
"$PY" "$T323/work/build_axes323.py" "$RUN/out/axes328" "$T322/out/profile_rank.json" "$RUN/out/axes328f" 1.2 3 > "$RUN/logs/axes328f.log" 2>&1
echo "[JOB] filter rc=$? files=$(ls "$RUN/out/axes328f" | wc -l) lines=$(cat "$RUN/out/axes328f"/*.xyz | wc -l)"
( cd "$RUN/out/axes328f" && md5sum *.xyz ) > "$RUN/out/axes328f.md5"
diff -rq "$T323/out/axes323" "$RUN/out/axes328f" > "$RUN/out/axes328f_vs_axes323.diff" 2>&1
echo "[JOB] vs axes323: diff lines=$(wc -l < "$RUN/out/axes328f_vs_axes323.diff") files_same=$([ -s "$RUN/out/axes328f_vs_axes323.diff" ] && echo no || echo yes)"
echo "[JOB] complete $(date -u +%FT%TZ)"
