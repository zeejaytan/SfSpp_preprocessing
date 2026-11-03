set -euo pipefail
NEW=${NEW:?}
PREV=${PREV:?}
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
RUNID=$(date -u +%Y%m%d-%H%M)_${NEW:0:7}_t69-pota-seat
RUN=$RUNS/$RUNID
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
mkdir -p $RUN/logs $RUN/out $RUN/instruments
git -C $CANON fetch --no-tags origin '+refs/heads/*:refs/remotes/origin/*' > $RUN/logs/fetch.log 2>&1 || true
git -C $CANON rev-parse --verify --quiet ${NEW}^{commit} >/dev/null || { echo 'commit missing'; exit 2; }
git -C $CANON show ${NEW}:.scratch/juglet-breaklines/stage69/submit69c.sbatch > $RUN/submit.sbatch
chmod +x $RUN/submit.sbatch
cat > $RUN/run.json <<EOF
{
  "runid": "$RUNID",
  "commit": "$NEW",
  "tag": "t69-pota-seat",
  "ticket": "69",
  "part": "C",
  "prev_run": "$PREV",
  "what": "Pot A seating, floor 50, two arms: POTA18 (shipped lanes, sphere 1.8/resample 1.9) and POTA09 (densified lanes, 0.9/0.95). Same harness, same patch, same surfaces, same axes; only the lane set differs, and both lane sets come from one preprocessing job.",
  "gate": "each arm 8/8 pieces and 15/15 joins",
  "submitted_by": "ticket-69 worker"
}
EOF
cd $RUN
sbatch --export=ALL,NEW=$NEW,PREV=$PREV submit.sbatch
echo RUN=$RUN
