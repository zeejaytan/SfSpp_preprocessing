#!/bin/bash
# Ticket 322: Pot G diagnostic -- is it the new extra lines? Two arms, two repeats each:
#   G_K1 = axes322 line 0 only; G_MX = axes322 line 0 + axes320 lines 1-2.
# Derived from the t322-potG run (itself the 319 Pot G run with axes322).
set -euo pipefail
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
SRC=$RUNS/20261110-0420_d628fc0_t322-potG
A322=$RUNS/20261110-0415_d628fc0_t322-axes/out/axes322
A320=$RUNS/20261108-1350_e556fc8_t318a-axes/out/axes320
RUN=$RUNS/$(date +%Y%m%d-%H%M)_d628fc0_t322-potG-diag
mkdir -p "$RUN"/{logs,out,score,trees,work/axes_k3,work/axes_k1,work/axes_mx}
( cd "$SRC/work" && cp -r *.py arm67.sh shim inc_src "$RUN/work/" )
for f in "$A322"/Pot_G_Piece_*_Axis.xyz; do
  b=$(basename "$f")
  head -n 1 "$f" > "$RUN/work/axes_k1/$b"
  { head -n 1 "$f"; sed -n 2,3p "$A320/$b"; } > "$RUN/work/axes_mx/$b"
done
sed -e "s#--job-name=t322-potG#--job-name=t322-gdiag#" \
    -e "s#--cpus-per-task=24#--cpus-per-task=32#" \
    -e 's#^stage_arm "\${POT}_K3" "MM" "\$WORK/axes_k3"#stage_arm "${POT}_K1" "MM" "$WORK/axes_k1"\nstage_arm "${POT}_MX" "MM" "$WORK/axes_mx"#' \
    -e 's#"\${POT}_K3R1" "\${POT}_K3R2"#"${POT}_K1R1" "${POT}_K1R2" "${POT}_MXR1" "${POT}_MXR2"#' \
    -e "s#^\# Ticket 322: pot end-to-end.*#\# Ticket 322: Pot G diagnostic, arms K1 (axes322 line 0) and MX (axes322 line 0 + axes320 lines 1-2).#" \
    "$SRC/submit.sbatch" > "$RUN/submit.sbatch"
grep -q 'stage_arm "${POT}_MX"' "$RUN/submit.sbatch"
[ "$(grep -c '_K1R1" "${POT}_K1R2" "${POT}_MXR1' "$RUN/submit.sbatch")" = 2 ]
cat > "$RUN/run.json" <<EOF
{"runid": "$(basename "$RUN")", "ticket": 322, "pot": "G", "tag": "t322-potG-diag",
 "commit": "d628fc0 + uncommitted working tree", "arms": {"G_K1": "axes322 line 0", "G_MX": "axes322 line 0 + axes320 lines 1-2"},
 "axes322": "$A322", "axes320": "$A320", "template": "$SRC"}
EOF
JID=$(cd "$RUN" && sbatch --parsable submit.sbatch)
printf "%s\t%s\t%s\t%s\t\t\n" "$(basename "$RUN")" "$JID" "d628fc0" "t322-potG-diag" >> "$RUNS/index.tsv"
echo "$(basename "$RUN") $JID"
