#!/bin/bash
# harvest small t68 job-2 outputs; compare D190 lanes with t66's
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1535_ffcb350_t68-densify
T66=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom
cd $RUN
echo "--- D190 vs t66 lanes/surfaces (md5 same?)"
for f in $T66/*; do b=$(basename $f); a=$(md5sum < $f | cut -c1-32); d=$(md5sum < outD190/geom/$b 2>/dev/null | cut -c1-32); [ "$a" = "$d" ] && s=same || s=DIFF; echo "$b $s"; done | sort -k2 | awk '{print $2}' | uniq -c
for f in $T66/*; do b=$(basename $f); a=$(md5sum < $f | cut -c1-32); d=$(md5sum < outD190/geom/$b | cut -c1-32); [ "$a" != "$d" ] && echo "DIFF $b"; done
tar czf harvest_t68c.tar.gz run.json binaries.md5 logs score out outD190/geom outD095/geom outD190/pieces66.tsv outD095/pieces66.tsv axes68
md5sum harvest_t68c.tar.gz
