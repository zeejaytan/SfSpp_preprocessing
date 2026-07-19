#!/bin/bash
module load Apptainer
cd /data/gpfs/projects/punim2657/sfs_preprocessing/build
apptainer exec --bind /data:/data /data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif bash -c "cmake .. && make AxisExtractionHeadless -j4"
