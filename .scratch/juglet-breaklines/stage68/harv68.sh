#!/bin/bash
# harvest small t68 Part A outputs (logs, scores, result dirs) as a tarball on stdout-free path
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1523_4b516be_t68-axis-method
cd $RUN
tar czf $RUN/harvest_t68a.tar.gz run.json logs score out axes68 work/logs/binary_F20O.log work/logs/binary_F20N.log
md5sum $RUN/harvest_t68a.tar.gz
grep -n -i -E "pair|LCS|candidate|pruned|root" work/logs/binary_F20N.log | head -60
