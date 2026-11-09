#!/bin/bash
# Ticket 323: build axes323 on a compute node, then (afterok) ten pot end-to-end jobs and one Juglet job.
# Pots: derived from that pot's ticket 319 run (arms <POT>_MO authors' axes control + <POT>_K3, two
# repeats each); the only change is AX_318 -> axes323 (head -n 3 is a no-op: axes323 has <= 3 lines).
# Juglet: derived from t320b-juglet; only AX_320 -> axes323. Prints "<pot> <runid> <jobid>".
set -euo pipefail
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
T322=$RUNS/20261110-0415_d628fc0_t322-axes/out
STAMP=$(date +%Y%m%d-%H%M)
AXRUN=$RUNS/${STAMP}_d628fc0_t323-axes
AX323=$AXRUN/out/axes323
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$AXRUN"/{logs,out,work}
cp "$HERE/build_axes323.py" "$AXRUN/work/"
cat > "$AXRUN/submit.sbatch" <<EOF
#!/bin/bash
#SBATCH --job-name=t323-axes
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --output=$AXRUN/logs/axes323_%j.out
# Ticket 323: axes323 = axes322 lines kept by the pre-registered rule (tau 1.2, at most 3 lines).
set -euo pipefail
/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3 $AXRUN/work/build_axes323.py $T322/axes322 $T322/profile_rank.json $AX323 1.2 3
md5sum $AX323/*.xyz > $AXRUN/out/axes323.md5
EOF
cat > "$AXRUN/run.json" <<EOF
{"runid": "$(basename "$AXRUN")", "ticket": 323, "tag": "t323-axes", "commit": "d628fc0",
 "inputs": ["$T322/axes322", "$T322/profile_rank.json"], "rule": "tau 1.2, kmax 3", "out": "$AX323"}
EOF
BJ=$(cd "$AXRUN" && sbatch --parsable submit.sbatch)
printf "%s\t%s\t%s\t%s\t\t\n" "$(basename "$AXRUN")" "$BJ" d628fc0 t323-axes >> "$RUNS/index.tsv"
echo "axes $(basename "$AXRUN") $BJ"

for P in A B C D E F G H I J; do
  SRC=$RUNS/20261109-1426_ecd5bb8_t319-pot$P
  RUN=$RUNS/${STAMP}_d628fc0_t323-pot$P
  mkdir -p "$RUN"/{logs,out,score,trees,work/axes_k3}
  ( cd "$SRC/work" && cp -r *.py arm67.sh shim inc_src "$RUN/work/" )
  sed -e "s#^AX_318=.*#AX_318=$AX323#" \
      -e "s#--job-name=t319-pot$P#--job-name=t323-pot$P#" \
      -e "s#^\# Ticket 319:.*#\# Ticket 323: pot end-to-end, MO control + axes323 (cost-ratio rule), two repeats; derived from $SRC.#" \
      "$SRC/submit.sbatch" > "$RUN/submit.sbatch"
  grep -q "^AX_318=$AX323" "$RUN/submit.sbatch"
  grep -q '_MOR1' "$RUN/submit.sbatch"
  cat > "$RUN/run.json" <<EOF
{"runid": "$(basename "$RUN")", "ticket": 323, "pot": "$P", "tag": "t323-pot$P", "commit": "d628fc0",
 "axes": "$AX323", "arms": ["${P}_MOR1", "${P}_MOR2", "${P}_K3R1", "${P}_K3R2"], "template": "$SRC",
 "depends_on": "$BJ"}
EOF
  JID=$(cd "$RUN" && sbatch --parsable --dependency=afterok:$BJ submit.sbatch)
  printf "%s\t%s\t%s\t%s\t\t\n" "$(basename "$RUN")" "$JID" d628fc0 "t323-pot$P" >> "$RUNS/index.tsv"
  echo "$P $(basename "$RUN") $JID"
done

SRC=$RUNS/20261110-0320_41494d0_t320b-juglet
RUN=$RUNS/${STAMP}_d628fc0_t323-juglet
mkdir -p "$RUN"/{logs,out,score,trees,work}
( cd "$SRC/work" && cp -r *.py *.sh *.tmpl shim inc_src "$RUN/work/" 2>/dev/null || true )
for f in stage67_inputs.py patch_guard67.py mk_inc.py arm67.sh; do test -e "$RUN/work/$f" || { echo "missing $f" >&2; exit 1; }; done
sed -e "s#^AX_320=.*#AX_320=$AX323#" \
    -e "s#--job-name=t320b-juglet#--job-name=t323-juglet#" \
    -e "s#^\# Ticket 320b:.*#\# Ticket 323: Juglet E2E, F20O control vs F20K3 on axes323; derived from $SRC.#" \
    "$SRC/submit.sbatch" > "$RUN/submit.sbatch"
grep -q "^AX_320=$AX323" "$RUN/submit.sbatch"
cat > "$RUN/run.json" <<EOF
{"runid": "$(basename "$RUN")", "ticket": 323, "pot": "Juglet", "tag": "t323-juglet", "commit": "d628fc0",
 "axes": "$AX323", "arms": ["F20O_r1", "F20K3_r1", "F20O_r2", "F20K3_r2"], "template": "$SRC",
 "depends_on": "$BJ"}
EOF
JID=$(cd "$RUN" && sbatch --parsable --dependency=afterok:$BJ submit.sbatch)
printf "%s\t%s\t%s\t%s\t\t\n" "$(basename "$RUN")" "$JID" d628fc0 t323-juglet >> "$RUNS/index.tsv"
echo "JUG $(basename "$RUN") $JID"
