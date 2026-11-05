#!/bin/bash
# Ticket 307 Stage C2: re-run ticket 302's MATLAB unit parity gate (bar 1e-9) against the
# current working tree (the COST_PRUNE switch added this ticket).
set -euo pipefail
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
SCP="/c/Windows/System32/OpenSSH/scp.exe"
TICKET=C:/PR/SfSpp_preprocessing
S302=$TICKET/.scratch/pota-repro/302-stage
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
COMMIT=$(git -C "$TICKET" rev-parse --short=7 HEAD)
TS=$("$SSH" spartan 'date -u +%Y%m%d-%H%M')
RUNID="${TS}_${COMMIT}_t307c-matlab-unit"
RUN="$RUNS/$RUNID"
echo "RUNID=$RUNID"
"$SSH" spartan "mkdir -p $RUN/logs $RUN/work $RUN/out"
cd "$TICKET"
rm -rf sfs_axes/__pycache__
cat > "$S302/run.json.t307" <<EOF
{
  "ticket": "307-paper-fidelity-axis-set",
  "gate": "C2: ticket 302 MATLAB unit parity, rel tol 1e-9, plus the Python regression tests",
  "commit": "$COMMIT",
  "note": "same instrument as 302's gate 1; sfs_axes uploaded from the working tree with the 307 COST_PRUNE switch"
}
EOF
"$SCP" "$S302/run.json.t307" "spartan:$RUN/run.json"
"$SCP" "$S302/submit302_unit.sbatch" "spartan:$RUN/submit.sbatch"
"$SCP" "$S302/gen302_unit_inputs.py" "$S302/unit302.m" "$S302/compare302_unit.py" "spartan:$RUN/work/"
"$SCP" -r sfs_axes "spartan:$RUN/work/"
OUT=$("$SSH" spartan "cd $RUN && md5sum submit.sbatch work/sfs_axes/*.py && sbatch --parsable submit.sbatch")
echo "$OUT"
JOB=$(echo "$OUT" | tail -1 | tr -d ' ')
echo "JOB=$JOB RUN=$RUN"
printf '%s\t%s\t%s\tt307c-matlab-unit\t\t\n' "$RUNID" "$JOB" "$COMMIT" > "$S302/ix.t307"
"$SCP" "$S302/ix.t307" "spartan:$RUN/index_row.tsv"
"$SSH" spartan "cat $RUN/index_row.tsv >> $RUNS/index.tsv"
rm -f "$S302/run.json.t307" "$S302/ix.t307"
echo done
