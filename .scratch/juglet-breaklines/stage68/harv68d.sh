#!/bin/bash
# harvest t68 job-3 (D2X) small outputs
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1546_6761aed_t68-densify2x
cd $RUN
sacct -j 34268623 -P -o JobID,JobName,State,ExitCode,Elapsed,MaxRSS
tar czf harvest_t68d.tar.gz run.json logs score out outD2X/geom outD2X/pieces66.tsv
md5sum harvest_t68d.tar.gz
