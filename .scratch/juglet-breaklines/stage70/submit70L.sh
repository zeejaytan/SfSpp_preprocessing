set -uo pipefail
BR=70-multi-axis-potsac
CAN=/data/gpfs/projects/punim2657/sfs_preprocessing
ROOT=/data/gpfs/projects/punim2657/SfSpp
git -C $CAN fetch -q origin $BR
C=$(git -C $CAN rev-parse FETCH_HEAD)
G7=$(echo $C | cut -c1-7)
TS=$(date +%Y%m%d-%H%M)
RUN=$ROOT/runs/"$TS"_"$G7"_t70-refine-live
mkdir -p $RUN/logs $RUN/out $RUN/work
git -C $CAN archive $C sfs_axes .scratch/juglet-breaklines/stage70 | tar -x -C $RUN/work
echo "RUN $RUN"
echo "COMMIT $C"
cat > $RUN/run.json <<'JEOF'
{
  "ticket": "70-multi-axis-potsac",
  "repo": "zeejaytan/SfSpp_preprocessing",
  "branch": "70-multi-axis-potsac",
  "commit": "__C__",
  "tag": "t70-refine-live",
  "part": "stage 2b: corpus match with live method-2 refine (arm L0, seed 0) + cost diagnostic on refined axes",
  "corpus": "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp (read-only)",
  "arms": "L0 step=10 no truncation seed 0, SFS_AXES_REFINE_NOOP=0",
  "match": "<=5 deg direction and <=2 mm radial position; edge gate 25 deg under GT poses",
  "submitted": true
}
JEOF
sed -i "s/__C__/$C/" $RUN/run.json
cat > $RUN/submit.sbatch <<'SEOF'
#!/bin/bash
#SBATCH --job-name=t70-live
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# submit.sbatch -- ticket 70 stage 2.  Submitted FROM the run dir.  Appends no index.tsv row.
set -uo pipefail
RUN=$SLURM_SUBMIT_DIR
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
C=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
W=$RUN/work
echo "=== t70 stage 2 job $SLURM_JOB_ID on $(hostname) at $(date -u +%FT%TZ)"
md5sum $W/sfs_axes/*.py $W/.scratch/juglet-breaklines/stage70/corpus70.py $W/.scratch/juglet-breaklines/stage70/cost70.py >> $RUN/logs/provenance.log 2>&1
ls $C/Axes | wc -l >> $RUN/logs/provenance.log 2>&1
export SFS_AXES_REFINE_NOOP=0
$PY $W/.scratch/juglet-breaklines/stage70/corpus70.py $C $RUN/out --jobs 8 --arms L0 2>&1 | tee $RUN/logs/corpus70.stdout
RC=${PIPESTATUS[0]}
$PY $W/.scratch/juglet-breaklines/stage70/cost70.py $C $RUN/out L0 2>&1 | tee $RUN/logs/cost70.stdout
RC2=${PIPESTATUS[0]}
echo "cost70 rc=$RC2"
echo "corpus70 rc=$RC"
echo "=== finished $(date -u +%FT%TZ)"
exit $RC
SEOF
chmod +x $RUN/submit.sbatch
echo SUBMIT
cd $RUN && sbatch submit.sbatch
