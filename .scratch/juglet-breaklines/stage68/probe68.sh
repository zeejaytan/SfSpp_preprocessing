#!/bin/bash
# read-only probe: t66 geom layout, axis files, python
G=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom
D=/data/gpfs/projects/punim2657/Dataset
ls -la "$G" | head -40
for f in "$G"/*Piece_2*; do echo "== $f"; head -c 400 "$f" | head -12; done
ls -la "$D"/Axes/Juglet/ "$D"/Juglet_GT/ "$D"/Mesh/Juglet/ 2>&1 | head -40
ls -la "$D"/Axes/ | head
cat "$D"/Axes/Juglet/Juglet_Piece_2_Axis.xyz
ls /data/gpfs/projects/punim2657/ | head -40
ls -d /data/gpfs/projects/punim2657/*/Juglet_Dataset_20260916 /data/gpfs/projects/punim2657/Juglet_Dataset_20260916 2>&1
which python3; python3 -c "import numpy, scipy; print(numpy.__version__, scipy.__version__)" 2>&1
