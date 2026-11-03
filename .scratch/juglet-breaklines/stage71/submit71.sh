#!/bin/bash
# submit71.sh -- build one run directory and sbatch it. Run on the Spartan login node.
# Upload this directory (costs71.py, b1_synthetic.py, corpus71.py, submit71.sh,
# submit71.sbatch) and run: bash submit71.sh
# If origin/71-find-the-real-objective exists, the run is archived from that commit.
# Otherwise sfs_axes comes from origin/70-multi-axis-potsac and these scripts are copied.
# The corpus is never written.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
CAN=/data/gpfs/projects/punim2657/sfs_preprocessing
ROOT=/data/gpfs/projects/punim2657/SfSpp
BR=71-find-the-real-objective
FB=70-multi-axis-potsac
git -C "$CAN" fetch -q origin "$BR" || true
if git -C "$CAN" rev-parse --verify --quiet "refs/remotes/origin/$BR" >/dev/null; then
  C=$(git -C "$CAN" rev-parse "refs/remotes/origin/$BR")
  MODE=branch
else
  git -C "$CAN" fetch -q origin "$FB"
  C=$(git -C "$CAN" rev-parse "refs/remotes/origin/$FB")
  MODE=upload
fi
G7=$(echo "$C" | cut -c1-7)
TS=$(date +%Y%m%d-%H%M)
RUNID="${TS}_${G7}_t71-objective"
RUN="$ROOT/runs/$RUNID"
mkdir -p "$RUN/logs" "$RUN/out" "$RUN/work"
if [ "$MODE" = branch ]; then
  git -C "$CAN" archive "$C" sfs_axes .scratch/juglet-breaklines/stage71 | tar -x -C "$RUN/work"
else
  git -C "$CAN" archive "$C" sfs_axes | tar -x -C "$RUN/work"
  mkdir -p "$RUN/work/.scratch/juglet-breaklines/stage71"
  cp -f "$HERE/costs71.py" "$HERE/b1_synthetic.py" "$HERE/corpus71.py" \
    "$RUN/work/.scratch/juglet-breaklines/stage71/"
fi
cp -f "$HERE/submit71.sbatch" "$RUN/submit.sbatch"
cat > "$RUN/run.json" <<EOF
{
  "ticket": "71-find-the-real-objective",
  "tag": "t71-objective",
  "sfs_axes_commit": "$C",
  "scripts": "$MODE",
  "refine": "noop",
  "seeds": 20,
  "step": 10,
  "truncation": false,
  "fit_step": 1,
  "corpus": "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp (read-only)",
  "match": "5 deg and 2 mm radial, released line 1 against any line of that seed"
}
EOF
chmod +x "$RUN/submit.sbatch"
jobid=$(cd "$RUN" && sbatch --parsable submit.sbatch)
jobid=${jobid%%;*}
INDEX="$ROOT/runs/index.tsv"
(
  flock -w 30 9
  printf '%s\t%s\t%s\t%s\t\t\n' "$RUNID" "$jobid" "$C" "t71-objective" >> "$INDEX"
) 9>>"$ROOT/runs/.index.lock"
echo "RUN $RUN"
echo "JOB $jobid"
echo "MODE $MODE"
echo "COMMIT $C"
echo "POLL scripts/slurm_poll.sh $jobid"
