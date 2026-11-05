#!/bin/bash
# Ticket 307 Stage C4 launcher: Juglet F20 with our axes at the shipped 307 default.
set -euo pipefail
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
SCP="/c/Windows/System32/OpenSSH/scp.exe"
TICKET=C:/PR/SfSpp_preprocessing
S305=$TICKET/.scratch/pota-repro/305-stage
S307=$TICKET/.scratch/pota-repro/307-stage
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
COMMIT=$(git -C "$TICKET" rev-parse --short=7 HEAD)
TS=$("$SSH" spartan 'date -u +%Y%m%d-%H%M')
RUNID="${TS}_${COMMIT}_t307d-jug"
RUN="$RUNS/$RUNID"
echo "RUNID=$RUNID"
"$SSH" spartan "mkdir -p $RUN/logs $RUN/work $RUN/out $RUN/score"
cd "$TICKET"
rm -rf sfs_axes/__pycache__
cat > "$S307/run.json.t307d" <<EOF
{
  "ticket": "307-paper-fidelity-axis-set",
  "stage": "C4: Juglet, one arm, F20 floor (authors' F20O vs ours F20N, 3 repeats each)",
  "commit": "$COMMIT",
  "axes": "ours at the shipped 307 default: paper chain, walls whole (truncate=0), cost prune ON, seed 0",
  "note": "F20 harness is 305-stage/jug305.sbatch verbatim; only __JAXDIR__ is substituted"
}
EOF
"$SCP" "$S307/run.json.t307d" "spartan:$RUN/run.json"
"$SCP" "$S307/submit307d.sbatch" "spartan:$RUN/submit.sbatch"
"$SCP" "$S305/axes305.py" "spartan:$RUN/work/"
sed 's/\r$//' "$S305/jug305.sbatch" > /tmp/jug305_LF.sbatch
"$SCP" /tmp/jug305_LF.sbatch "spartan:$RUN/work/jug305.tmpl"
"$SCP" -r sfs_axes "spartan:$RUN/work/"
echo -n "$COMMIT" > /tmp/code_commit.txt
"$SCP" /tmp/code_commit.txt "spartan:$RUN/work/code_commit.txt"
OUT=$("$SSH" spartan "cd $RUN && file work/jug305.tmpl && md5sum submit.sbatch work/sfs_axes/*.py work/axes305.py && sbatch --parsable submit.sbatch")
echo "$OUT"
JOB=$(echo "$OUT" | tail -1 | tr -d ' ')
echo "JOB=$JOB RUN=$RUN"
printf '%s\t%s\t%s\tt307d-jug\t\t\n' "$RUNID" "$JOB" "$COMMIT" > /tmp/ix.t307d
"$SCP" /tmp/ix.t307d "spartan:$RUN/index_row.tsv"
"$SSH" spartan "cat $RUN/index_row.tsv >> $RUNS/index.tsv"
rm -f "$S307/run.json.t307d"
echo done
