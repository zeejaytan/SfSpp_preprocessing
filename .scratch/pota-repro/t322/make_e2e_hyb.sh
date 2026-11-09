#!/bin/bash
# Ticket 322 checkpoint 11: hybrid-axes end-to-end for the named pots, derived from the t322 axes322 run
# of the same pot (only the axes dir, job name and tag change). usage: make_e2e_hyb.sh <afterok-jobid> D [G ...]
set -euo pipefail
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
AXH=$RUNS/20261110-0415_d628fc0_t322-axes/out/axes_hyb
DEP=$1; shift
STAMP=$(date +%Y%m%d-%H%M)
for P in "$@"; do
  SRC=$RUNS/20261110-0420_d628fc0_t322-pot$P
  RUN=$RUNS/${STAMP}_d628fc0_t322hyb-pot$P
  mkdir -p "$RUN"/{logs,out,score,trees,work/axes_k3}
  ( cd "$SRC/work" && cp -r *.py arm67.sh shim inc_src "$RUN/work/" )
  sed -e "s#^AX_318=.*#AX_318=$AXH#" \
      -e "s#--job-name=t322-pot$P#--job-name=t322h-pot$P#" \
      -e "s#^\# Ticket 322: pot end-to-end.*#\# Ticket 322 hybrid: axes322 line 1 + axes320 lines 2..K, K=3, two repeats; derived from $SRC.#" \
      "$SRC/submit.sbatch" > "$RUN/submit.sbatch"
  grep -q "AX_318=$AXH" "$RUN/submit.sbatch"
  cat > "$RUN/run.json" <<EOF
{"runid": "$(basename "$RUN")", "ticket": 322, "pot": "$P", "tag": "t322hyb-pot$P",
 "commit": "d628fc0 (axes built from files: axes322 line 1 + axes320 lines, t322/build_hybrid.py)",
 "axes": "$AXH", "k": 3, "arms": ["${P}_K3R1", "${P}_K3R2"], "template": "$SRC"}
EOF
  JID=$(cd "$RUN" && sbatch --parsable --dependency=afterok:$DEP submit.sbatch)
  printf "%s\t%s\t%s\t%s\t\t\n" "$(basename "$RUN")" "$JID" "d628fc0" "t322hyb-pot$P" >> "$RUNS/index.tsv"
  echo "$P $(basename "$RUN") $JID"
done
