#!/bin/bash
# Build the ten t325 pot runs from the t323 pot templates: same job layout
# (4 arms = MO control + K3 top-3, two repeats each), axes pointing at the
# t325 byte-identical axes325 tree. Bucket: confirmation of bar 6.
set -uo pipefail
SRCROOT=/data/gpfs/projects/punim2657/SfSpp/runs
A325=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-1450_22151d0_t325-axes/out/axes325
STAMP=$(date -u +%Y%m%d-%H%M)
for P in A B C D E F G H I J; do
  S=$SRCROOT/20261110-0740_d628fc0_t323-pot$P
  D=$SRCROOT/${STAMP}_22151d0_t325-pot$P
  [ -d "$S" ] || { echo "missing $S"; exit 1; }
  mkdir -p "$D"/{logs,out,score,work}
  for f in submit.sbatch; do cp -p "$S/$f" "$D/$f"; done
  for f in acc305.py arm67.sh mk_inc.py patch_guard67.py score305.py score311_cpp.py stage305.py summarise311b.py render323.py; do
    cp -p "$S/work/$f" "$D/work/$f"
  done
  mkdir -p "$D/work"/{axes_k3,build,inc_src,shim,logs}
  sed -i -e "s|^#SBATCH --job-name=t323-pot$P|#SBATCH --job-name=t325-pot$P|" \
         -e "s|AX_318=.*axes323|AX_318=$A325|" "$D/submit.sbatch"
  cat > "$D/run.json" <<EOF
{
 "runid": "$(basename $D)",
 "ticket": 325,
 "tag": "t325-pot$P",
 "commit": "22151d0 (ticket 325 branch)",
 "purpose": "bar 6 confirmation: ten-pot assembly with axes325, which is byte-identical to axes323 (verified 172/172 on 2026-11-10)",
 "template": "20261110-0740_d628fc0_t323-pot$P",
 "arms": ["$P" "_MOR1", "_MOR2", "_K3R1", "_K3R2"],
 "docs": "STAMP=$STAMP"
}
EOF
  echo "$D"
done
