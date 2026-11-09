#!/bin/bash
# Ticket 322: one end-to-end run per pot on axes322, derived mechanically from the ticket 319
# run of that pot (same lanes, NAMED, NP, FLOOR, staging, scorer, K=3 = head -n 3).
# Changes against 319: AX_318 -> axes322; the authors' _MO arm dropped (on record in 319);
# 24 CPUs / 96G (two concurrent arms instead of four). Prints "<pot> <runid> <jobid>".
set -euo pipefail
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
AX322=$RUNS/20261110-0415_d628fc0_t322-axes/out/axes322
STAMP=$(date +%Y%m%d-%H%M)
for P in "$@"; do
  SRC=$RUNS/20261109-1426_ecd5bb8_t319-pot$P
  RUN=$RUNS/${STAMP}_d628fc0_t322-pot$P
  mkdir -p "$RUN"/{logs,out,score,trees,work/axes_k3}
  ( cd "$SRC/work" && cp -r *.py arm67.sh shim inc_src "$RUN/work/" )
  sed -e "s#^AX_318=.*#AX_318=$AX322#" \
      -e "s#--job-name=t319-pot$P#--job-name=t322-pot$P#" \
      -e "s#--cpus-per-task=48#--cpus-per-task=24#" \
      -e "s#--mem=160G#--mem=96G#" \
      -e '/^stage_arm "\${POT}_MO"/d' \
      -e 's#"\${POT}_MOR1" "\${POT}_MOR2" "\${POT}_K3R1" "\${POT}_K3R2"#"${POT}_K3R1" "${POT}_K3R2"#' \
      -e "s#^\# Ticket 319:.*#\# Ticket 322: pot end-to-end on axes322 (profile-thickness ranking), K=3, two repeats; derived from $SRC.#" \
      "$SRC/submit.sbatch" > "$RUN/submit.sbatch"
  grep -q "AX_318=$AX322" "$RUN/submit.sbatch"
  ! grep -q '_MOR1' "$RUN/submit.sbatch"
  cat > "$RUN/run.json" <<EOF
{"runid": "$(basename "$RUN")", "ticket": 322, "pot": "$P", "tag": "t322-pot$P",
 "commit": "d628fc0 + uncommitted working tree (sfs_axes/profile.py, sfs_axes/potsac.py); code md5s in $RUNS/20261110-0415_d628fc0_t322-axes/out/axes322_code.md5",
 "axes": "$AX322", "k": 3, "arms": ["${P}_K3R1", "${P}_K3R2"], "template": "$SRC"}
EOF
  JID=$(cd "$RUN" && sbatch --parsable submit.sbatch)
  printf "%s\t%s\t%s\t%s\t\t\n" "$(basename "$RUN")" "$JID" "d628fc0" "t322-pot$P" >> "$RUNS/index.tsv"
  echo "$P $(basename "$RUN") $JID"
done
