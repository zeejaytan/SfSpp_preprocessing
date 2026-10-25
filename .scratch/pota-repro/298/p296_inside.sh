#!/usr/bin/env bash
# Ticket 296 assembly arm -- runs INSIDE sfs_pristine_assembly.sif.
# The pinned assembler (upstream 9195c01) is GUI-only and segfaults under Xvfb (diag job 32976970),
# so the batch shim hpc/tools/main_pristine_batch.cpp is compiled out-of-source against it and
# linked with the pristine objects -- upstream main.cpp with viewer statements removed, nothing else.
# Exactly the recipe of hpc/sbatch/run_pristine_pota.sbatch, except the dataset is bound to this
# run's own directory (the harness binds original_samples, which writes Result/ into the corpus).
set -euo pipefail
R=/p296run
BD=$(mktemp -d /tmp/p296-build-XXXXXX) && cd "$BD"
echo "[P296] build dir $BD (fresh; /tmp is shared between jobs on a node, never reuse a name)"
echo "[P296] inside $(hostname); cwd $(pwd)"
cmake /opt/sfs-pristine -DCMAKE_BUILD_TYPE=Release > "$R/logs/shim_cmake.log" 2>&1
make -j8 > "$R/logs/shim_make.log" 2>&1
echo "[P296] pristine objects built: $(ls CMakeFiles/Hierarchy-Clear.dir/*.o 2>/dev/null | wc -l)"
D=CMakeFiles/Hierarchy-Clear.dir
DEFS=$(grep "^CXX_DEFINES" $D/flags.make | cut -d= -f2- | tr " " "\n" | grep -v "GOOGLE_GLOG_DLL_DECL" | tr "\n" " ")
INCS=$(grep "^CXX_INCLUDES" $D/flags.make | cut -d= -f2-)
FLAGS=$(grep "^CXX_FLAGS" $D/flags.make | cut -d= -f2-)
g++ ${DEFS} ${INCS} ${FLAGS} -I/opt/sfs-pristine -I/opt/sfs-pristine/class \
    -c /workspace/hpc/tools/main_pristine_batch.cpp -o CMakeFiles/shim.o
LINK=$(cat $D/link.txt)
LINK=${LINK//CMakeFiles\/Hierarchy-Clear.dir\/main.cpp.o/CMakeFiles\/shim.o}
LINK=${LINK//\/opt\/sfs-pristine\/build\/CMakeFiles\/Hierarchy-Clear.dir\/main.cpp.o/CMakeFiles\/shim.o}
LINK=${LINK/-o Hierarchy-Clear/-o Hierarchy-Batch}
echo "$LINK" > "$R/logs/shim_link.txt"
eval "$LINK"
ls -l Hierarchy-Batch | tee "$R/logs/binary_ls.txt"
md5sum Hierarchy-Batch | tee "$R/logs/binary.md5"
# what the pinned assembler reads, straight out of the pinned tree (no git: dubious ownership)
sed -n '1379,1400p' /opt/sfs-pristine/class/data_path.h > "$R/logs/data_path_potA.txt"
grep -n "Breakline" /opt/sfs-pristine/class/data_path.h >> "$R/logs/data_path_potA.txt"
grep -n "data_type\|string path" /opt/sfs-pristine/class/data_path.h | head -4 >> "$R/logs/data_path_potA.txt"
set +e
time ./Hierarchy-Batch 8 > "$R/logs/assembly.log" 2>&1
RC=$?
set -e
echo "assembly exit $RC" > "$R/out/assembly_exit.txt"
echo "[P296] assembly exit $RC"
grep -E "Total number|Sherd accuracy|Edge accuracy|Result save finish|Saving transformation|co-first" \
    "$R/logs/assembly.log" | tail -n 12 | tee "$R/out/summary.txt" || true
ls -la /Dataset/SfS_pp/Result/ > "$R/out/result_ls.txt" 2>&1 || true
cd / && rm -rf "$BD"
exit 0
