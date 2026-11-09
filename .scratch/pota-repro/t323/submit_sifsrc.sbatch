#!/bin/bash
#SBATCH --job-name=t323-sifsrc
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --output=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0730_d628fc0_t323-sifsrc/logs/sifsrc_%j.out
# Ticket 323: copy the assembler source out of the pristine SIF so it can be diffed
# against the laptop checkout of structure-from-sherds-pp at 9a613b5.
set -euo pipefail
apptainer() { /apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer "$@"; }
R=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0730_d628fc0_t323-sifsrc
SIF=/data/gpfs/projects/punim2657/sfs_main/sfs_pristine_assembly.sif
md5sum "$SIF" > "$R/out/sif.md5"
apptainer exec "$SIF" bash -c 'cd /opt/sfs-pristine && ls -la && tar czf - --exclude=build --exclude=.git .' > "$R/out/sfs-pristine-src.tgz"
apptainer exec "$SIF" bash -c 'cd /opt/sfs-pristine && find . -path ./build -prune -o -path ./.git -prune -o -type f \( -name "*.cpp" -o -name "*.h" -o -name "*.txt" \) -print0 | xargs -0 md5sum' > "$R/out/src.md5"
if apptainer exec "$SIF" test -d /opt/sfs-pristine/.git; then
  apptainer exec "$SIF" git -C /opt/sfs-pristine log -1 --format='%H %s' > "$R/out/git_head.txt" 2>&1 || true
fi
wc -l "$R/out/src.md5"
echo done
