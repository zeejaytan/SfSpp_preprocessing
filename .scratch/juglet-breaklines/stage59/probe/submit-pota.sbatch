#!/bin/bash
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=01:00:00
#SBATCH --job-name=t59potA
#SBATCH --output=logs/pota-%j.out

set -euo pipefail
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/__RUNID__
cd "$RUN"
mkdir -p logs out
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
S0=/data/gpfs/projects/punim2657/SfSpp/runs/20261102-1144_638504b_t59-breakstop-stage0

cat > run.json <<EOF
{
  "runid": "__RUNID__",
  "jobid": "${SLURM_JOB_ID}",
  "commit": "638504b",
  "branch": "59-break-surface-stop-rule",
  "tag": "t59-pota-relabel",
  "purpose": "ticket 59 Stage-0 addendum: Pot A label sweep (td 10-30, mf 0.01/0.02, slab along 4/8/12mm) -- is the 99%-fracture collapse a range/threshold artifact; plus corrected Juglet per-piece nanmedian medians; reads stage-0 npz read-only",
  "inputs": {"stage0_labels_readonly": "$S0/out/labels"},
  "params": {"tds_deg": [10,15,20,25,30], "min_fracs": [0.01,0.02], "slab_along_max_mm": [4,8,12], "b_ray_probe": "td20 mf0.02 along8, L=2.5*t_est+1"}
}
EOF

md5sum work/pota_relabel.py > work/pota_relabel.md5
echo "=== pota relabel start $(date) ==="
"$PY" work/pota_relabel.py --stage0-dir "$S0" --out out 2>&1 | tee logs/pota.log
rc=${PIPESTATUS[0]}
echo "=== pota exit $rc $(date) ==="
ls -la out/ | head -20
printf '%s\t%s\t%s\t%s\t\t\n' "__RUNID__" "${SLURM_JOB_ID}" "638504b" "t59-pota-relabel" >> /data/gpfs/projects/punim2657/SfSpp/runs/index.tsv
exit "$rc"
