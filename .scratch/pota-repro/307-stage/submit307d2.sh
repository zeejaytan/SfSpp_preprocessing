#!/bin/bash
# submit307d2.sh -- fix the failed t307d-jug run dir and resubmit (run 20261105-0422).
# The first attempt died at rc=4 "guard patch failed rc=2": the launcher had copied sfs_axes to
# work/ (not work/code) and had not copied patch_guard67.py / mk_inc.py / stage67_inputs.py /
# acc305.py / score58.py at all, so jug305's body had nothing to call.
set -euo pipefail
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
SCP="/c/Windows/System32/OpenSSH/scp.exe"
TICKET=C:/PR/SfSpp_preprocessing
S305=$TICKET/.scratch/pota-repro/305-stage
S307=$TICKET/.scratch/pota-repro/307-stage
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0422_e6adf69_t307d-jug
cd "$TICKET"
for f in stage67_inputs.py score58.py; do
  sed 's/\r$//' "$S305/$f" > "$S307/helpers/$f"
done
"$SSH" spartan "mkdir -p $RUN/work/code"
"$SCP" -q "$S307/helpers/arm67.sh" "$S307/helpers/patch_guard67.py" "$S307/helpers/mk_inc.py" "$S307/helpers/stage67_inputs.py" "$S307/helpers/acc305.py" "$S307/helpers/score58.py" "spartan:$RUN/work/"
rm -rf sfs_axes/__pycache__
"$SCP" -q -r sfs_axes "spartan:$RUN/work/code/"
"$SSH" spartan "cd $RUN && file work/arm67.sh work/score58.py && md5sum work/patch_guard67.py work/code/sfs_axes/potsac.py && sbatch --parsable submit.sbatch"
