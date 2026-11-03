set -euo pipefail
NEW=${NEW:?}
PREV=${PREV:?}
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
RUNID=$(date -u +%Y%m%d-%H%M)_${NEW:0:7}_t69-pota-axes
RUN=$RUNS/$RUNID
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
mkdir -p $RUN/logs $RUN/out $RUN/instruments
git -C $CANON fetch --no-tags origin '+refs/heads/*:refs/remotes/origin/*' > $RUN/logs/fetch.log 2>&1 || true
git -C $CANON rev-parse --verify --quiet ${NEW}^{commit} >/dev/null || { echo 'commit missing'; exit 2; }
git -C $CANON show ${NEW}:.scratch/juglet-breaklines/stage69/submit69d.sbatch > $RUN/submit.sbatch
chmod +x $RUN/submit.sbatch
cat > $RUN/run.json <<'EOF'
{
  "runid": "@RUNID@",
  "commit": "@NEW@",
  "tag": "t69-pota-axes",
  "ticket": "69",
  "part": "C",
  "prev_run": "@PREV@",
  "what": "Pot A seating at the shipped floor 50, two arms, CORRECTED axes: POTA18C (corpus lanes, sphere 1.8/resample 1.9) and POTA09C (corpus lanes at 0.9/0.95). Same harness, same patch, same surfaces, same CORPUS axes (the corpus Axes dir, the ones the t67 PACTL and t68 GPA50 controls read); only the lane set differs, and both lane sets come from one preprocessing job.",
  "why": "submit69c (job 34275210) returned 7/8 and 12/15 in BOTH arms because it staged Dataset/Axes/Pot_A instead of the corpus axes; pieces 06 and 08 move 24.7 and 15.6 deg between those files. That run is superseded and its gate is not evidence about density.",
  "gate": "POTA18C must be 8/8 pieces and 15/15 joins (reproducing PACTL); then POTA09C answers whether 0.9 mm lanes cost Pot A anything",
  "submitted_by": "ticket-69 worker"
}
EOF
sed -i "s|@RUNID@|$RUNID|; s|@NEW@|$NEW|; s|@PREV@|$PREV|" $RUN/run.json
cd $RUN
sbatch --export=ALL,NEW=$NEW,PREV=$PREV submit.sbatch
echo RUN=$RUN