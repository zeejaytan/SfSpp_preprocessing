#!/bin/bash
J1=/data/gpfs/projects/punim2657/SfSpp/runs/20261027-0323_41de06c_t25-dump-p2p3
cd "$J1"/instruments || exit 1
echo "=== brace-expansions used by the instruments:"
grep -h -o '[$]{[^}]*}' run_cell25.sh stage_piece_p25.sh | sort | uniq -c | sort -rn | head -40
echo
echo "=== the buggy cat-file line in the submit script:"
grep -n 'cat-file' "$J1"/submit_25.sbatch
echo
echo "=== preflight tools"
AP=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF=/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
for f in "$AP" "$SIF" "$PY"; do [ -e "$f" ] && echo "ok $f" || echo "MISSING $f"; done
"$PY" -c "import numpy, matplotlib, scipy; print('py modules ok', numpy.__version__, matplotlib.__version__, scipy.__version__)" 2>&1 | tail -2
echo
echo "=== preflight inputs"
CDIR=/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset
BOOT=/data/gpfs/projects/punim2657/SfSpp/runs/20261027-0055_d8af9d2_p07-juglet-stage1/out/boot
for p in Juglet_Piece_2 Juglet_Piece_3 Juglet_Piece_5 Juglet_Piece_7; do
  c="$CDIR/Point/Juglet/"$p"_Point.pcd"
  m="$CDIR/Mesh/Juglet/"$p"_Mesh.obj"
  a="$BOOT/"$p"_boot_Axis.xyz"
  printf '%s cloud=%s mesh=%s axis=%s points=%s md5c=%s axis1=%s\n' "$p" "$([ -e "$c" ] && echo y || echo n)" "$([ -e "$m" ] && echo y || echo n)" "$([ -e "$a" ] && echo y || echo n)" "$(grep -m1 POINTS "$c" | awk '{print $2}')" "$(md5sum "$c" | cut -d' ' -f1)" "$(head -c 80 "$a" 2>/dev/null | tr -d '\n')"
done
echo
echo "=== archive works for both commits"
cd /data/gpfs/projects/punim2657/sfs_preprocessing || exit 1
for c in 41de06c07e0c917626f19c2ac9759feebd5b6ff3 d543e18627c02354732bd9e7f33eb21d8dbbbce2; do
  n=$(git archive "$c" | tar -t | wc -l)
  h=$(git archive "$c" mesh_processing_headless.cpp | tar -xO | md5sum | cut -d' ' -f1)
  echo "$(echo "$c" | cut -c1-7) files=$n cpp_md5=$h"
done
echo
echo "=== stale build dirs / leftover state in the two run dirs"
for d in "$J1" /data/gpfs/projects/punim2657/SfSpp/runs/20261027-0323_41de06c_t25-dump-p5p7; do echo "$d: $(ls "$d" | tr '\n' ' ')"; done
echo "=== index tail"
tail -3 /data/gpfs/projects/punim2657/SfSpp/runs/index.tsv
