#!/bin/bash
# Ticket 322 checkpoint 13: K=1 end-to-end on axes322 (first line only), one job per pot, two repeats.
# Derived from that pot's t322-pot<X> run; only head -n 3 -> head -n 1, the arm labels and the job name change.
set -euo pipefail
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
STAMP=$(date +%Y%m%d-%H%M)
for P in "$@"; do
  SRC=$RUNS/20261110-0420_d628fc0_t322-pot$P
  RUN=$RUNS/${STAMP}_d628fc0_t322k1-pot$P
  mkdir -p "$RUN"/{logs,out,score,trees,work/axes_k1}
  ( cd "$SRC/work" && cp -r *.py arm67.sh shim inc_src "$RUN/work/" )
  sed -e "s#--job-name=t322-pot$P#--job-name=t322k1-pot$P#" \
      -e 's#head -n 3 "\$f"#head -n 1 "$f"#' \
      -e 's#axes_k3#axes_k1#g' \
      -e 's#_K3#_K1#g' \
      -e "s#^\# Ticket 322: pot end-to-end.*#\# Ticket 322 checkpoint 13: K=1 (axes322 first line only), two repeats; derived from $SRC.#" \
      "$SRC/submit.sbatch" > "$RUN/submit.sbatch"
  grep -q 'head -n 1 "$f"' "$RUN/submit.sbatch"
  if grep -q '_K3\|axes_k3\|head -n 3' "$RUN/submit.sbatch"; then echo "K3 left in $RUN" >&2; exit 1; fi
  cat > "$RUN/run.json" <<EOF
{"runid": "$(basename "$RUN")", "ticket": 322, "pot": "$P", "tag": "t322k1-pot$P",
 "commit": "d628fc0 (axes322 built by the profile ranker, now t322/profile_ranker.patch)",
 "axes": "$RUNS/20261110-0415_d628fc0_t322-axes/out/axes322", "k": 1,
 "arms": ["${P}_K1R1", "${P}_K1R2"], "template": "$SRC"}
EOF
  JID=$(cd "$RUN" && sbatch --parsable submit.sbatch)
  printf "%s\t%s\t%s\t%s\t\t\n" "$(basename "$RUN")" "$JID" "d628fc0" "t322k1-pot$P" >> "$RUNS/index.tsv"
  echo "$P $(basename "$RUN") $JID"
done
