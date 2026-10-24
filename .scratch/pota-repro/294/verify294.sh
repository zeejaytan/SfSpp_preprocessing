#!/usr/bin/env bash
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261025-0340_0f8a4a4_p294-pictures
echo "=== GEOMETRY_DELETED head/tail ==="
head -12 $RUN/out/GEOMETRY_DELETED.txt
tail -3 $RUN/out/GEOMETRY_DELETED.txt
echo "=== big files outside bin ==="
find $RUN -type f -size +1M ! -path "*/bin/*" | wc -l
echo "=== stage remains ==="; ls -d $RUN/stage/* 2>/dev/null | wc -l
echo "=== geom remains ==="; ls -1 $RUN/out/geom 2>/dev/null | wc -l
echo "=== png md5 ==="; cat $RUN/out/png.md5
echo "=== classify ==="; cut -f1,2,4 $RUN/out/classify.tsv
echo "=== source ==="; cat $RUN/out/source.md5
