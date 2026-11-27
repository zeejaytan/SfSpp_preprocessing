#!/bin/bash
#SBATCH --job-name=t14-j01
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
# Ticket 14: both diagnostic parts in ONE job on a compute node.
#   Part A  j01_lobe14.py            J01 mesh + o1_off lobe render, and the 143-stem
#                                    (286 face) own-vs-author wall comparison.
#   Part B  j01_selector_trace14.py  8 wall arms through the frozen SHIP selector,
#                                    per-candidate trace before keep_lines(tau=1.2).
# Read-only: imports the frozen selector from the t03-ship run tree, writes only
# under this run directory. Submit from the run directory:
#   sbatch --parsable submit.sbatch
# Poll from the laptop: scripts/slurm_poll.sh <JOBID>
set -uo pipefail

RUN="${SLURM_SUBMIT_DIR:?submit from the run directory}"
SHIP=/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship
export SFS_IMPL="$SHIP/work/impl_t03"
export PYTHONPATH="$SFS_IMPL:$SHIP/work:$RUN/work/t14"
export MPLBACKEND=Agg
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-1}"
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
NP="${SLURM_CPUS_PER_TASK:-8}"

cd "$RUN" || exit 2
mkdir -p logs evidence renders out work/t14
[ -f evidence/jobs.tsv ] || printf 'job_id\tstate\texit_code\n' > evidence/jobs.tsv
printf '%s\tSUBMITTED\t\n' "$SLURM_JOB_ID" >> evidence/jobs.tsv

echo "[JOB] runid=$(basename "$RUN") job=$SLURM_JOB_ID py=$PY np=$NP start=$(date -u +%FT%TZ)"
$PY -c 'import numpy, scipy, matplotlib; print("numpy", numpy.__version__, "scipy", scipy.__version__, "mpl", matplotlib.__version__)' \
    > logs/env.txt 2>&1 || { echo "[JOB] FATAL python env"; exit 3; }
cat logs/env.txt

# Provenance of the two scripts actually executed (the committed .scratch copies,
# staged here by the dispatcher; the sha256 is what the ticket cites).
{ for f in work/t14/j01_lobe14.py work/t14/j01_selector_trace14.py; do
    printf '%s\t%s\t%s\n' "$(sha256sum "$f" | cut -d' ' -f1)" "$(stat -c %s "$f")" "$f"
  done; } > evidence/sources.tsv
cat evidence/sources.tsv

rc=0
$PY work/t14/j01_lobe14.py --run "$RUN" --jobs "$NP" > logs/j01_lobe14.log 2>&1 || rc=$?
echo "[JOB] PartA j01_lobe14 rc=$rc at $(date -u +%FT%TZ)"
tail -n 6 logs/j01_lobe14.log

if [ "$rc" -eq 0 ]; then
  $PY work/t14/j01_selector_trace14.py --run "$RUN" --jobs "$NP" > logs/j01_selector_trace14.log 2>&1 || rc=$?
  echo "[JOB] PartB j01_selector_trace14 rc=$rc at $(date -u +%FT%TZ)"
  tail -n 12 logs/j01_selector_trace14.log
fi

if [ "$rc" -eq 0 ]; then
  # ---- deliverable checks: the files the ticket names, with their row counts ----
  n_off=0; n_tr=0
  [ -s evidence/corpus_offwall_143.tsv ] && n_off=$(( $(wc -l < evidence/corpus_offwall_143.tsv) - 1 ))
  [ -s evidence/j01_arm_trace.tsv ] && n_tr=$(( $(wc -l < evidence/j01_arm_trace.tsv) - 1 ))
  printf 'file\tdata_rows\texpected\n' > evidence/counts.tsv
  printf 'evidence/corpus_offwall_143.tsv\t%s\t286\n' "$n_off" >> evidence/counts.tsv
  printf 'evidence/j01_arm_trace.tsv\t%s\t8\n' "$n_tr" >> evidence/counts.tsv
  cat evidence/counts.tsv

  # a tab requirement that silently became CSV is the classic failure here
  if grep -q ',' evidence/corpus_offwall_143.tsv evidence/j01_arm_trace.tsv; then
    echo "[JOB] FATAL comma found in a TSV"; rc=9
  fi
  case "$(head -c 4 evidence/corpus_offwall_143.tsv)" in
    stem) : ;;
    *) echo "[JOB] FATAL corpus header does not start with stem"; rc=9 ;;
  esac
  [ "$n_off" -eq 286 ] || { echo "[JOB] FATAL corpus rows=$n_off not 286"; rc=9; }
  [ "$n_tr" -eq 8 ] || { echo "[JOB] FATAL trace rows=$n_tr not 8"; rc=9; }

  printf 'name\tpath\tdescription\n' > evidence/renders.tsv
  for spec in \
    "J01_mesh_and_s1_lobe_3d.png|J01 mesh with o0, o1_on and o1_off in XY/XZ/YZ and an oblique 3D view, donor line and GT axis overlaid" \
    "J01_selector_trace.png|minimum donor-line angle at each selector stage for the 8 arms, and cost/cost[0] of the best-donor candidate against the tau=1.2 cut"; do
    f="${spec%%|*}"; d="${spec#*|}"
    if [ -s "renders/$f" ]; then
      printf '%s\t%s\t%s\n' "${f%.png}" "renders/$f" "$d" >> evidence/renders.tsv
      echo "[JOB] render renders/$f $(stat -c %s "renders/$f") bytes"
    else
      echo "[JOB] FATAL missing renders/$f"; rc=8
    fi
  done
  cat evidence/renders.tsv
fi

echo "[JOB] done rc=$rc at $(date -u +%FT%TZ)"
exit "$rc"
