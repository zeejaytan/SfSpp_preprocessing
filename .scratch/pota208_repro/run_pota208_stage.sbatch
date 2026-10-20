#!/bin/bash
# POTA-208 seating: pristine scorer @ b56bc80 (restore guards), ORIG control + fresh
# pristine-line bundle (pota208_bundle_v0). Recipe = run_pota_restore_e2e.sbatch;
# verdict matcher fixed (space-stripped compare).
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --time=12:00:00
#SBATCH --nodes=1 --ntasks-per-node=1 --cpus-per-task=8 --mem=32G
#SBATCH --job-name=pota208_stage
#SBATCH --output=pota208_stage_%j.out
#SBATCH --error=pota208_stage_%j.err
set -uo pipefail
E2E=/data/gpfs/projects/punim2657/pota208_e2e
SRC="${E2E}/src"
HEAD_WANT="b56bc80d788fd10110d2a821097a29bcdba759e6"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
ORIG="/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
MSIF="/data/gpfs/projects/punim2657/sfs_main/sfs_pristine_assembly.sif"
RUNDIR="${E2E}/pota208_run_${SLURM_JOB_ID}"
BUN="/data/gpfs/projects/punim2657/pota208_bundle_v0/SfS_pp"
GTSTUB="/data/gpfs/projects/punim2657/pota29/gt_stub.cpp"
echo "=== POTA-208 SEATING (pristine scorer + pristine-line bundle) ==="; date; hostname
[ "$(git -C "${SRC}" rev-parse HEAD)" = "${HEAD_WANT}" ] || { echo WRONG-HEAD; exit 1; }
[ -z "$(git -C "${SRC}" status --porcelain | grep -v '^??')" ] || { echo TREE-DIRTY; exit 1; }
grep -q "P22FIX" "${SRC}/class/feature_matching.cpp" && { echo CURE-P22FIX; exit 1; } || echo "absent OK: P22FIX"
grep -q "P22FIX2" "${SRC}/class/ranking_system.cpp" && { echo CURE-P22FIX2; exit 1; } || echo "absent OK: P22FIX2"
grep -q "POTA38" "${SRC}/class/feature_matching.cpp" && { echo CURE-POTA38; exit 1; } || echo "absent OK: POTA38"
grep -q "axis_angle_ > 0.610" "${SRC}/class/feature_matching.cpp" && { echo FORK-0610; exit 1; } || echo "absent OK: 0.610"
grep -q "0\.2, 20\.0" "${SRC}/class/ranking_system.cpp" && { echo FORK-02; exit 1; } || echo "absent OK: 0.2"
grep -q "axis_angle_ > 0.436" "${SRC}/class/feature_matching.cpp" || { echo MISSING-0436; exit 1; }
echo "present OK: 0.436"
grep -q "PRISTINE-RESTORE" "${SRC}/class/axis_estimation.cpp" || { echo KEEP-AXIS; exit 1; }
grep -q "PRISTINE-RESTORE" "${SRC}/class/data_structure.cpp" || { echo KEEP-PCD; exit 1; }
echo "present OK: PRISTINE-RESTORE keeps"
[ -f "${MSIF}" ] || { echo SIF-MISSING; exit 1; }
[ -f "${GTSTUB}" ] || { echo GTSTUB-MISSING; exit 1; }
echo "### bundle guards (fresh pristine-line v0)"
[ "$(ls "${BUN}/Breaklines"/*.pcd | wc -l)" = "16" ] || { echo BUN-BL-NE-16; exit 1; }
[ "$(ls "${BUN}/Surfaces"/*.xyz | wc -l)" = "16" ] || { echo BUN-SURF-NE-16; exit 1; }
[ "$(ls "${BUN}/Axes"/*.xyz | wc -l)" = "8" ] || { echo BUN-AXES-NE-8; exit 1; }
[ "$(ls "${BUN}/Mesh"/*.obj | wc -l)" = "8" ] || { echo BUN-MESH-NE-8; exit 1; }
md5sum "${BUN}/Breaklines"/*.pcd | sort > "${E2E}/pota208_bun_v0_md5.txt"
echo "bundle OK; md5 recorded"
mkdir -p "${RUNDIR}"
build_and_run() {
  local SRC="$1" TAG="$2" DS="$3" ARM="$4"
  local SHIM="${SRC}/hpc/tools/main_pristine_batch.cpp"
  echo "===== ${TAG}-${ARM} ====="
  time "${APPTAINER}" exec --bind /data:/data --bind "${DS}:/Dataset/SfS_pp" "${MSIF}" bash -c '
set -euo pipefail
RUNDIR="'"${RUNDIR}"'"
SRC="'"${SRC}"'" TAG="'"${TAG}"'" ARM="'"${ARM}"'" SHIM="'"${SHIM}"'" GTSTUB="'"${GTSTUB}"'"
rm -rf /tmp/pb-208-"${TAG}"-"${ARM}" && mkdir -p /tmp/pb-208-"${TAG}"-"${ARM}" && cd /tmp/pb-208-"${TAG}"-"${ARM}"
grep -q "P22FIX" "${SRC}/class/feature_matching.cpp" && { echo "CURE-MARKER-IN-CONTAINER"; exit 1; } || echo "container absent OK: P22FIX/P22FIX2/POTA38"
grep -q "P22FIX2" "${SRC}/class/ranking_system.cpp" && { echo "CURE-MARKER-IN-CONTAINER"; exit 1; } || true
grep -q "POTA38" "${SRC}/class/feature_matching.cpp" && { echo "CURE-MARKER-IN-CONTAINER"; exit 1; } || true
grep -q "axis_angle_ > 0.610" "${SRC}/class/feature_matching.cpp" && { echo "FORK-GATE-IN-CONTAINER"; exit 1; } || echo "container absent OK: 0.610/0.2"
grep -q "0\.2, 20\.0" "${SRC}/class/ranking_system.cpp" && { echo "FORK-02-IN-CONTAINER"; exit 1; } || true
grep -q "axis_angle_ > 0.436" "${SRC}/class/feature_matching.cpp" || { echo "PRISTINE-GATE-MISSING-IN-CONTAINER"; exit 1; }
cmake "${SRC}" -DCMAKE_BUILD_TYPE=Release >"${RUNDIR}/${TAG}_${ARM}_cmake.log" 2>&1
make -j8 Hierarchy-Clear >"${RUNDIR}/${TAG}_${ARM}_make.log" 2>&1
D="CMakeFiles/Hierarchy-Clear.dir"
DEFS=$(grep "^CXX_DEFINES" $D/flags.make | cut -d= -f2- | tr " " "\n" | grep -v "GOOGLE_GLOG_DLL_DECL" | tr "\n" " " || true)
INCS=$(grep "^CXX_INCLUDES" $D/flags.make | cut -d= -f2- || true)
FLAGS=$(grep "^CXX_FLAGS" $D/flags.make | cut -d= -f2- || true)
SHIM_INC="-I${SRC} -I${SRC}/class"
g++ ${DEFS} ${INCS} ${FLAGS} ${SHIM_INC} -c "${SHIM}" -o CMakeFiles/shim.o
if [ -f "${SRC}/class/ground_truth_debug.h" ]; then
g++ ${DEFS} ${INCS} ${FLAGS} ${SHIM_INC} -c "${GTSTUB}" -o CMakeFiles/gt_stub.o
GTSTUB_OBJ="CMakeFiles/gt_stub.o"
else
echo "GTSTUB-SKIPPED-OK (pristine tree: no GroundTruthDebugger)"
GTSTUB_OBJ=""
fi
LINK=$(cat $D/link.txt)
LINK=${LINK//CMakeFiles\/Hierarchy-Clear.dir\/main_headless_correct.cpp.o/CMakeFiles\/shim.o}
LINK=${LINK//CMakeFiles\/Hierarchy-Clear.dir\/main.cpp.o/CMakeFiles\/shim.o}
LINK=${LINK//\/opt\/sfs-pristine\/build\/CMakeFiles\/Hierarchy-Clear.dir\/main.cpp.o/CMakeFiles\/shim.o}
case "${LINK}" in *shim.o*) echo "LINK-SHIM-OK";; *) echo "LINK-SHIM-MISS"; exit 1;; esac
case "${LINK}" in *main_headless_correct*) echo "LINK-FORKMAIN-LEAK"; exit 1;; *) echo "LINK-FORKMAIN-ABSENT-OK";; esac
OBJ=$(echo "${LINK}" | grep -o "[^ ]*shim\.o" | head -1)
[ -n "${OBJ}" ] && [ -f "${OBJ}" ] || { echo "SHIM-O-MISSING: ${OBJ}"; exit 1; }
echo "SHIM-O-FOUND: ${OBJ}"
LINK=${LINK//CMakeFiles\/shim.o/CMakeFiles\/shim.o ${GTSTUB_OBJ}}
LINK=${LINK/-o Hierarchy-Clear/-o Hierarchy-Batch-208}
eval "${LINK}"
strings ./Hierarchy-Batch-208 | grep -q "adaptive beam search TOP_k" && { echo "DRIVER-FORKMAIN-LEAK"; exit 1; } || echo "DRIVER-SHIM-OK"
mkdir -p /Dataset/SfS_pp/Result
time ./Hierarchy-Batch-208 8 >"${RUNDIR}/${TAG}_${ARM}_binary.log" 2>&1
rc=$?
grep -E "Total number|Sherd accuracy|Edge accuracy" "${RUNDIR}/${TAG}_${ARM}_binary.log" | tail -n 6 || true
mkdir -p "${RUNDIR}/${TAG}_${ARM}_Result_snapshot"
cp -pr /Dataset/SfS_pp/Result/. "${RUNDIR}/${TAG}_${ARM}_Result_snapshot/" 2>/dev/null || true
for rd in results_*/; do [ -d "$rd" ] && cp -pr "$rd" "${RUNDIR}/${TAG}_${ARM}_cwd_${rd%/}" || true; done
NT=$(ls "${RUNDIR}/${TAG}_${ARM}_Result_snapshot"/T_*.txt 2>/dev/null | wc -l)
echo "SNAPSHOT-T-COUNT=${NT}"
[ "${NT}" -eq 8 ] || { echo "SNAPSHOT-NOT-8-FAIL"; exit 1; }
rm -rf /Dataset/SfS_pp/Result
exit ${rc}
' > "${RUNDIR}/${TAG}_${ARM}_outer.log" 2>&1
  echo "${TAG}-${ARM} container exit $?"
}
tally() {
  grep -a -E "Sherd accuracy|Edge accuracy" "${RUNDIR}/$1_$2_binary.log" | tail -2
}
build_and_run "${SRC}" L "${ORIG}" orig
build_and_run "${SRC}" L "${BUN}" fresh
echo "### L-arm tallies (ORIG control must read 8/8+15/15 or VOID)"; echo "--- L-orig ---"; tally L orig; echo "--- L-fresh ---"; tally L fresh
echo "### pruned/hypothesis lines (informational)"
for ARM in orig fresh; do echo "--- L_${ARM} ---"; grep -a -E "Total number|pruned|accuracy|Accuracy|hypothesis|Hypothes" "${RUNDIR}/L_${ARM}_binary.log" | head -20 || true; done
SHERD_ORIG=$(grep -a "Sherd accuracy" "${RUNDIR}/L_orig_binary.log" | tail -1 || true)
EDGE_ORIG=$(grep -a "Edge accuracy" "${RUNDIR}/L_orig_binary.log" | tail -1 || true)
echo "ORIG-SHERD-LINE: ${SHERD_ORIG}"
echo "ORIG-EDGE-LINE: ${EDGE_ORIG}"
SHERD_NOSPC=${SHERD_ORIG// /}; EDGE_NOSPC=${EDGE_ORIG// /}; if [[ "${SHERD_NOSPC}" == *"8/8"* && "${EDGE_NOSPC}" == *"15/15"* ]]; then echo "VERDICT: PASS (ORIG control 8/8+15/15)"; else echo "VERDICT: VOID-or-FAIL (ORIG control not 8/8+15/15)"; fi
SHERD_FRESH=$(grep -a "Sherd accuracy" "${RUNDIR}/L_fresh_binary.log" | tail -1 || true)
EDGE_FRESH=$(grep -a "Edge accuracy" "${RUNDIR}/L_fresh_binary.log" | tail -1 || true)
echo "FRESH-SHERD-LINE: ${SHERD_FRESH}"
echo "FRESH-EDGE-LINE: ${EDGE_FRESH}"
SHERD_FNOSPC=${SHERD_FRESH// /}; EDGE_FNOSPC=${EDGE_FRESH// /}; if [[ "${SHERD_FNOSPC}" == *"8/8"* && "${EDGE_FNOSPC}" == *"15/15"* ]]; then echo "FRESH-VERDICT: 8/8+15/15"; else echo "FRESH-VERDICT: diagnostic below bar (see lines above)"; fi
echo "=== POTA-208 seating DONE ==="; date
