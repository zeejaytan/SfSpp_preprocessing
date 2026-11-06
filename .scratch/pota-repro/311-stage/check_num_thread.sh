#!/usr/bin/env bash
set -euo pipefail
SSH="/c/Windows/System32/OpenSSH/ssh.exe -T -o BatchMode=yes"
$SSH spartan '
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF=/data/gpfs/projects/punim2657/sfs_main/sfs_pristine_assembly.sif
$APT exec $SIF grep -rn "NUMBER_OF_THREAD" /opt/sfs-pristine/class/ || true
'
