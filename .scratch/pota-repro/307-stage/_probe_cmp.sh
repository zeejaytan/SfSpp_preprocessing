#!/bin/bash
R=/data/gpfs/projects/punim2657/SfSpp/runs
echo "== runs matching moom"
ls -d $R/*moom* 2>/dev/null
echo "== 305 notrunc seed1 line counts"
wc -l $R/20261105-0455_9c5eec2_t305-axes-stage0c/out/notrunc/axes_seed1/*.xyz
echo "== md5 305 notrunc s1"
md5sum $R/20261105-0455_9c5eec2_t305-axes-stage0c/out/notrunc/axes_seed1/*.xyz | awk '{print $1" "$2}'
echo "== md5 307 base_s1"
md5sum $R/20261105-0406_e6adf69_t307a-axes/out/pota/base_s1/*.xyz | awk '{print $1" "$2}'
