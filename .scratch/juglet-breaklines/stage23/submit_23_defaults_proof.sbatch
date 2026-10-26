#!/usr/bin/env bash
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --job-name=__JOBNAME__
#SBATCH --time=00:30:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --output=logs/slurm-%j.out
#
# ticket 23: the defaults proof, both pots. Runs no mesh stage: it reads the surfaces the grid run
# already kept (arm A, A2, A_old) and compares point sets. The earlier analysis job lost the Juglet
# rows because defaults_proof23.py wrote one path per invocation and the second pot truncated the
# first; SFS_PROOF_OUT names a file per pot now.
set -uo pipefail
RUN=__RUNDIR__
GRID=__GRIDRUN__
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
INSTR=$RUN/instruments
CELLROOT=$GRID/out/cells
JUG="Juglet_Piece_1 Juglet_Piece_2 Juglet_Piece_3 Juglet_Piece_4 Juglet_Piece_5 Juglet_Piece_6 Juglet_Piece_7 Juglet_Piece_8 Juglet_Piece_9"
POT="Pot_A_Piece_01 Pot_A_Piece_02 Pot_A_Piece_03 Pot_A_Piece_04 Pot_A_Piece_05 Pot_A_Piece_06 Pot_A_Piece_07 Pot_A_Piece_08"
cd "$RUN" || exit 1
mkdir -p logs out
say() { echo "[$(date +%H:%M:%S)] $*"; }
say "job ${SLURM_JOB_ID:-local} defaults proof over $GRID"

for pot in Juglet Pot_A; do
  case "$pot" in Juglet) P="$JUG" ;; *) P="$POT" ;; esac
  SFS_PROOF_OUT="$RUN/out/defaults_proof23_$pot.tsv" "$PY" "$INSTR/defaults_proof23.py" "$CELLROOT" "$pot" $P \
    > "out/defaults_proof_$pot.log" 2>&1
  say "$pot exit=$? rows=$(wc -l < "out/defaults_proof23_$pot.tsv" 2>/dev/null) -- $(tail -1 "out/defaults_proof_$pot.log")"
done

head -1 out/defaults_proof23_Juglet.tsv > out/defaults_proof23.tsv
tail -n +2 out/defaults_proof23_Juglet.tsv >> out/defaults_proof23.tsv
tail -n +2 out/defaults_proof23_Pot_A.tsv >> out/defaults_proof23.tsv
say "combined rows=$(wc -l < out/defaults_proof23.tsv)"

awk -F'\t' 'NR==1{next}
  {k=$1"/"$2"/"$3; if($4=="A_old") o[k]=$10" / "$12"  npts "$5" vs "$6;
                 else if($4=="A2") a[k]=$10" / "$12"  npts "$5" vs "$6}
  END{print "pot/piece/surface\tA_vs_A_old max mm (A->old / old->A) npts\tA_vs_A2 max mm (A->A2 / A2->A) npts";
      for(k in o) printf "%s\t%s\t%s\n", k, o[k], a[k]}' out/defaults_proof23.tsv | sort \
  > out/defaults_proof_summary.txt
column -t -s$'\t' out/defaults_proof_summary.txt | head -40

say "run dir bytes: $(du -sb "$RUN" | awk '{print $1}')"
printf "%s\t%s\t%s\t%s\t\t\n" "$(basename "$RUN")" "${SLURM_JOB_ID:-local}" "__NEWCOMMIT__" "p23-defaults-proof" \
  >> /data/gpfs/projects/punim2657/SfSpp/runs/index.tsv
say "done"
