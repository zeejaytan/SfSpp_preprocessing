#!/bin/bash
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=03:00:00
#SBATCH --job-name=t59s0
#SBATCH --output=logs/probe-%j.out

set -euo pipefail
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/__RUNID__
cd "$RUN"
mkdir -p logs out
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3

cat > run.json <<EOF
{
  "runid": "__RUNID__",
  "jobid": "${SLURM_JOB_ID}",
  "commit": "638504b",
  "branch": "59-break-surface-stop-rule",
  "tag": "t59-breakstop-stage0",
  "purpose": "ticket 59 Stage 0: mesh-structural labels + four signals (roughness, thickness pairing, accumulated turn, t55-claim agreement), 9 Juglet pieces + Pot A control; no pipeline change",
  "inputs": {
    "meshes_juglet": "sfs_preprocessing/Dataset/Mesh/Juglet/Juglet_Piece_{1..9}_Mesh.obj",
    "meshes_pot_a": "sfs_preprocessing/Dataset/Mesh/Pot_A/Pot_A_Piece_{01..08}_Mesh.obj",
    "t55_claims_readonly": "SfSpp/runs/20261101-2004_05be12c_t55-worness07-breaklines/out/geom"
  },
  "params": {
    "dihedral_deg_primary": 10.0,
    "dihedral_deg_sens": [8.0, 15.0],
    "min_comp_area_frac_primary": 0.03,
    "min_comp_area_frac_sens": [0.02, 0.05],
    "ball_radii_mm": [1.0, 1.5, 2.0, 3.0],
    "geodesic_windows_mm": [2, 5, 10, "Lf=(pi/4)*Rf"],
    "slab": {"perp_mm": 0.75, "along_mm": [0.25, 4.0], "exit_dot_max": -0.5, "ray_max_t": 1.5},
    "src_cap_per_label": 800,
    "src_cap_pota": 150
  }
}
EOF

md5sum work/stage0_probe.py > work/probe.md5
echo "=== stage0 probe start $(date) ==="
"$PY" work/stage0_probe.py --out out 2>&1 | tee logs/probe.log
rc=${PIPESTATUS[0]}
echo "=== probe exit $rc $(date) ==="
ls -la out/ out/labels/ | head -50
printf '%s\t%s\t%s\t%s\t\t\n' "__RUNID__" "${SLURM_JOB_ID}" "638504b" "t59-breakstop-stage0" >> /data/gpfs/projects/punim2657/SfSpp/runs/index.tsv
exit "$rc"
