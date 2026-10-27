#!/bin/bash
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --time=03:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --output=logs/slurm-%j.out
# ticket 35 - mesh-side measurement of Juglet 1,2,3,5,7,9 and Pot_A 01,07.
# pure numpy: no container, no build.  Usage: submit35.sbatch RUN COMMIT [PYTHON]
set -uo pipefail

RUN="$1"
COMMIT="$2"
PY="${3:-python3}"
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing

cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" || exit 90
echo "host   $(hostname)"
echo "date   $(date -Is)"
echo "run    $RUN"
echo "commit $COMMIT"
echo "python $(command -v "$PY")"
"$PY" -c 'import sys, numpy; print("py", sys.version.split()[0], "numpy", numpy.__version__)' || exit 91

BUILD=$(mktemp -d /tmp/t35-build-XXXXXXXX) || exit 92
trap 'rm -rf "$BUILD"' EXIT
git -C "$CANON" fetch --quiet origin || exit 93
git -C "$CANON" archive "$COMMIT" | tar -x -C "$BUILD" || exit 94
INSTR="$BUILD/.scratch/juglet-breaklines/stage35/instruments/measure35.py"
if [ ! -s "$INSTR" ]; then echo "MISSING INSTRUMENT $INSTR"; exit 95; fi
echo "instrument $(md5sum "$INSTR")"

"$PY" "$INSTR" --out "$RUN/out"
rc=$?
echo "measure35 exit $rc"
echo "tables:"; ls -l "$RUN/out/tables" 2>/dev/null | tail -n +2 | awk '{print "  "$5" "$9}'
exit $rc
