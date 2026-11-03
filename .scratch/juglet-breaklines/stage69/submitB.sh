set -euo pipefail
NEW=ae5ad599b053f7a05724da87be8144eda0d097a3
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
RUNID=$(date -u +%Y%m%d-%H%M)_${NEW:0:7}_t69-density-panel
RUN=$RUNS/$RUNID
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
mkdir -p $RUN/logs $RUN/out
# pull the branch into the canonical checkout (fetch only; nothing edited there)
git -C $CANON fetch --no-tags origin '+refs/heads/*:refs/remotes/origin/*' > $RUN/logs/fetch.log 2>&1 || true
git -C $CANON rev-parse --verify --quiet ${NEW}^{commit} >/dev/null || { echo 'commit missing'; exit 2; }
git -C $CANON show ${NEW}:.scratch/juglet-breaklines/stage69/submit69b.sbatch > $RUN/submit.sbatch
chmod +x $RUN/submit.sbatch
cat > $RUN/run.json <<EOF
{
  "runid": "$RUNID",
  "commit": "ae5ad599b053f7a05724da87be8144eda0d097a3",
  "tag": "t69-density-panel",
  "ticket": "69",
  "stage": "all",
  "what": "Part B density panel (Pot A 8, Pot C 4, Pot D 10, Pot J 11) at sphere 1.8/resample 1.9 vs 0.9/0.95 on one staged surface pair per piece, plus the Part D byte-identity proof on Pot_A_Piece_01",
  "submitted_by": "ticket-69 worker"
}
EOF
cd $RUN
sbatch --export=ALL,NEW=${NEW},RUNID=$RUNID,STAGE=all submit.sbatch
echo RUN=$RUN
