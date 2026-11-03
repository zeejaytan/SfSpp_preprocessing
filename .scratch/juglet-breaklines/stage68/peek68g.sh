#!/bin/bash
# peek68g.sh -- GJ50 binary log + arm diagnostics of the guard proof-build
W=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1523_4b516be_t68-axis-method/guard68/work
grep -nE "SFS-NO-CANDIDATES|Total number|Segmentation|core dumped|Node Sequence|Sherd accuracy|Result save" $W/logs/binary_GJ50.log
echo "--- tail"; tail -4 $W/logs/binary_GJ50.log
echo "--- arm diffs (floor 50: expect empty)"; wc -c $W/logs/diff_GJ50.txt $W/logs/diff_GPA50.txt 2>/dev/null
grep -E "compile rc|link rc|binary md5|batch exit|variant md5|guarded base md5" $W/../logs/panel.log
echo "--- pristine vs archive"; grep -E "same|DIFF" $W/../logs/provenance.log | head -12
echo "--- canonical checkout"; git -C /data/gpfs/projects/punim2657/sfs_main/sfspreproc-docker status --porcelain | head -3; git -C /data/gpfs/projects/punim2657/sfs_main/sfspreproc-docker rev-parse HEAD
