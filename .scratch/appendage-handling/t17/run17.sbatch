#!/bin/bash
#SBATCH --job-name=t17_appendages
#SBATCH --partition=sapphire
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err

# Ticket 17: census of attached appendages + Juglet_Piece_1 handle ablation +
# the three eye-check renders, all in ONE compute-node job.  The run directory
# is a git archive of the ticket commit, so the scripts live at $T17 below and
# every output stays inside it.  Heavy work only on the compute node.

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?SLURM_SUBMIT_DIR not set}"

PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
T17=.scratch/appendage-handling/t17
T03=/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship/work
export SFS_IMPL="$T03/impl_t03"
export OMP_NUM_THREADS=1
export MPLBACKEND=Agg
export PYTHONHASHSEED=0

mkdir -p evidence renders logs

echo "== ticket 17 job =="
echo "host:    $(hostname)"
echo "jobid:   ${SLURM_JOB_ID:-none}"
echo "run dir: $PWD"
echo "python:  $PY"
"$PY" -c 'import sys, numpy, scipy, matplotlib; print("py", sys.version.split()[0], "numpy", numpy.__version__, "scipy", scipy.__version__, "mpl", matplotlib.__version__)'
echo

echo "== 1/3 census of 157 pieces =="
"$PY" "$T17/census_appendages17.py" --out evidence/appendage_census_157.tsv \
    --json logs/census17.json --jobs 8
echo

echo "== 2/3 Juglet_Piece_1 handle ablation =="
"$PY" "$T17/juglet1_ablation17.py" --t03 "$T03" \
    --out evidence/juglet1_handle_ablation.tsv --json logs/juglet1_ablation17.json
echo

echo "== 3/3 renders =="
"$PY" "$T17/render_appendages17.py" --outdir . --census evidence/appendage_census_157.tsv
echo

echo "== output checks =="
awk -F'\t' 'NR==1{print "census header cols="NF} NR>1{n++; if(NF!=18) bad++} END{print "census data rows="n" bad_cols="bad+0}' \
    evidence/appendage_census_157.tsv
awk -F'\t' 'NR==1{print "ablation header cols="NF} NR>1{n++; if(NF!=9) bad++} END{print "ablation data rows="n" bad_cols="bad+0}' \
    evidence/juglet1_handle_ablation.tsv
echo "renders.tsv lines=$(awk 'END{print NR}' evidence/renders.tsv)"
ls -l renders/*.png
cat evidence/juglet1_handle_ablation.tsv
echo
echo "census header: $(head -1 evidence/appendage_census_157.tsv)"
echo "flagged rows:  $(awk -F'\t' 'NR>1 && $18!="ok"' evidence/appendage_census_157.tsv | wc -l)"
echo "flag counts:"
awk -F'\t' 'NR>1{n=split($18,a,","); for(i=1;i<=n;i++) c[a[i]]++} END{for(k in c) print "  "k" "c[k]}' \
    evidence/appendage_census_157.tsv | sort

test "$(awk 'END{print NR}' evidence/appendage_census_157.tsv)" -eq 158 \
    || { echo "FAIL: census must have 158 lines (header + 157)"; exit 1; }
test "$(awk 'END{print NR}' evidence/juglet1_handle_ablation.tsv)" -ge 3 \
    || { echo "FAIL: ablation must have header + at least 2 arms"; exit 1; }
test "$(awk 'END{print NR}' evidence/renders.tsv)" -eq 3 \
    || { echo "FAIL: renders.tsv must list exactly 3 paths"; exit 1; }
test -s renders/Juglet_Piece_1_handle_and_walls.png
test -s renders/Pot_J_Piece_03_clusters_3d.png
test -s renders/Flagged_appendage_sherds_gallery.png

echo
echo "== ticket 17 job OK =="
