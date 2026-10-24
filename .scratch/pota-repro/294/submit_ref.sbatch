#!/usr/bin/env bash
#SBATCH --job-name=p294ref
#SBATCH --time=00:10:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --output=logs/slurm-%j.out
set -euo pipefail
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261025-0340_0f8a4a4_p294-pictures
cd "$RUN"
export OUT="$RUN/out"
ls /usr/bin/python3 && /usr/bin/python3 -c "import numpy; print(numpy.__version__)"
/usr/bin/python3 "$RUN/scripts/mesh_ref.py" | tee "$RUN/out/authors_to_mesh.txt"
echo REF_EXIT=${PIPESTATUS[0]}
