set -uo pipefail
BR=69-axis-density-corpus-check
CAN=/data/gpfs/projects/punim2657/sfs_preprocessing
ROOT=/data/gpfs/projects/punim2657/SfSpp
git -C $CAN fetch -q origin $BR
C=$(git -C $CAN rev-parse FETCH_HEAD)
G7=$(echo $C | cut -c1-7)
TS=$(date +%Y%m%d-%H%M)
RUN=$ROOT/runs/"$TS"_"$G7"_t69-axis-corpus
mkdir -p $RUN/logs $RUN/out $RUN/work
echo "RUN $RUN"
echo "COMMIT $C"
cat > $RUN/run.json <<'JEOF'
{
  "ticket": "69-axis-density-corpus-check",
  "repo": "zeejaytan/SfSpp_preprocessing",
  "branch": "69-axis-density-corpus-check",
  "commit": "__C__",
  "tag": "t69-axis-corpus",
  "part": "A: the ticket-68 axis estimators measured against the released Ground Truth Axes of all ten pots",
  "corpus": "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp (read-only)",
  "estimators": "rel0, relbest, nperp, nperpS1, npar, nparS1, pottS1, potsac_s0 -- FIXED across pots, no per-piece GT selection",
  "submitted": true
}
JEOF
sed -i "s/__C__/$C/" $RUN/run.json
cat > $RUN/submit.sbatch <<'SEOF'
#!/bin/bash
#SBATCH --job-name=t69-partA
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
# submit.sbatch -- ticket 69 Part A: every corpus piece that has a released GT axis (141)
# scored against the released axis and against six fixed estimators.  Submitted FROM the
# run dir (RUN=$SLURM_SUBMIT_DIR).  Appends no index.tsv row.
set -uo pipefail
RUN=$SLURM_SUBMIT_DIR
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
C=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
CAN=/data/gpfs/projects/punim2657/sfs_preprocessing
W=$RUN/work
echo "=== t69 Part A job $SLURM_JOB_ID on $(hostname) at $(date -u +%FT%TZ)"
git -C $CAN log --oneline -1 >> $RUN/logs/provenance.log 2>&1
md5sum $W/sfs_axes/*.py >> $RUN/logs/provenance.log 2>&1
md5sum $W/partA69.py >> $RUN/logs/provenance.log 2>&1
ls $C/Ground\ Truth\ Axes | wc -l >> $RUN/logs/provenance.log 2>&1
$PY $W/partA69.py $C $RUN/out --jobs 8 2>&1 | tee $RUN/logs/partA.stdout
RC=$?
echo "partA rc=$RC"
echo "=== finished $(date -u +%FT%TZ)"
SEOF
chmod +x $RUN/submit.sbatch
echo SUBMIT
cd $RUN && sbatch submit.sbatch
