#!/usr/bin/env bash
# ticket 30: create one part C arm run directory on Spartan, ship the instruments, submit it.
# The theta is in the directory name AND in run.json, which is the ticket's acceptance 4.
# usage: ship_arm.sh <sha7> <tag> <jobname> <walltime> <theta> <role> <pieces...>
#   e.g. ship_arm.sh 66c84dc t30-jc3p801 30jc3p801 04:00:00 3.801 test Juglet_Piece_1 ... Piece_9
set -uo pipefail
SHA=$1; TAG=$2; JOBNAME=$3; WTIME=$4; THETA=$5; ROLE=$6; shift 6
PIECES="$*"
SRC=$(cd "$(dirname "$0")" && pwd)
HOST=$SRC/_ship
ROOT=/data/gpfs/projects/punim2657/SfSpp/runs
RUNID=$(date -u +%Y%m%d-%H%M)_${SHA}_${TAG}
RUN=$ROOT/$RUNID
rm -rf "$HOST" && mkdir -p "$HOST/instruments"
cp -f "$SRC"/analyse30.py "$SRC"/measure_pair30.py "$SRC"/replica29.py "$SRC"/run_arm30.sh \
      "$SRC"/run_dump30.sh "$SRC"/stage_piece_p30.sh "$SRC"/submit30.sh \
      "$SRC"/submit_30_dump.sbatch.tmpl "$SRC"/submit_30_arm.sbatch.tmpl "$HOST/instruments/"
IFS=$' \t\n'
cat > "$HOST/run.json" <<JSON
{
  "ticket": "30-should-the-criterion-be-an-angle",
  "runid": "${RUNID}",
  "runs_root": "${ROOT}",
  "commit": "${SHA}",
  "instrument": "stage30: run_arm30.sh on the shipped binary plus measure_pair30.py's corrected pair statistic",
  "instrument_commit": "${SHA}",
  "job": "part C arm ${TAG}: pipeline at SFS_PAPER_THETA=${THETA} with everything else at defaults",
  "jobid": null,
  "index_tag": "${TAG}",
  "arm_role": "${ROLE}",
  "sfs_paper_theta": "${THETA}",
  "parameters": {
    "theta_deg": ${THETA},
    "role": "${ROLE}",
    "pieces": "$PIECES",
    "piece_count": $(echo $PIECES | wc -w),
    "unset_env": "SFS_SINGLE_CLUSTER, SFS_WINDOW_MODE, SFS_SPACING_POLICY",
    "set_env": "SFS_PAPER_THETA only",
    "edgeline": "each cell runs our own edgeline stage on the surfaces it wrote; Breakline_0 count only"
  },
  "inputs": {
    "corpus": "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp",
    "canonical": "/data/gpfs/projects/punim2657/sfs_preprocessing",
    "juglet_axes": "/data/gpfs/projects/punim2657/SfSpp/runs/20261027-0055_d8af9d2_p07-juglet-stage1/out/boot",
    "note": "read-only; md5 listing of every cloud, mesh and axis taken before and after, plus a full corpus tree listing"
  },
  "writes": ["out/arms/** surfaces and breaklines", "out/arms/armcells30.tsv", "out/arms/breaks30.tsv", "out/arms/measure30.tsv", "logs/**"],
  "geometry_deleted": "each cell's staged tree and edgestage, counted per extension into out/arms/geometry_counts.tsv and summarised in out/GEOMETRY_DELETED.txt"
}
JSON
python -c "import json,sys;json.load(open(sys.argv[1]));print('[SHIP] run.json parses')" "$HOST/run.json" || exit 3
if grep -lU $'\r' "$HOST"/instruments/* "$HOST"/run.json 2>/dev/null; then echo "[SHIP] FATAL CRLF"; exit 4; fi
echo "[SHIP] runid=$RUNID theta=$THETA role=$ROLE pieces=$(echo $PIECES | wc -w)"
ssh spartan "mkdir -p $RUN/logs $RUN/out" || exit 5
tar -C "$HOST" -czf - run.json instruments | ssh spartan "tar -xzf - -C $RUN" || exit 5
ssh spartan "cd $RUN && THETA=$THETA PIECES='$PIECES' ROLE=$ROLE bash instruments/submit30.sh $RUN $TAG $JOBNAME $WTIME $SHA submit_30_arm.sbatch.tmpl"
