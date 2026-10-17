#!/bin/bash
# POTA-58 PILOT STAGE (Pot F): cure-potA @ bffefb6, POT_F overlay, k=5/b=3 shim
# both arms, LINK-SHIM-OK + LINK-FORKMAIN-ABSENT-OK + DRIVER-SHIM-OK asserts.
# ORIG = shipped SfS_pp bundle (validity control: must reproduce 39's F ORIG
# 6/6+9/9 or the vehicle is void for F); fresh = pota58_bundle_F (39 F bundle
# COPY + paper-recipe flagger relaxed >=10pt, DATA-identical, gate carries over).
# Overlay mechanism: host-side untracked data_path file bind-mounted over
# /p40/asm/class/data_path.h INSIDE the container only. Zero patches to clones.
# Ticket 39/40/49 lanes are read-only reference; this job writes only
# pota58_* paths.
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --time=12:00:00
#SBATCH --nodes=1 --ntasks-per-node=1 --cpus-per-task=8 --mem=32G
#SBATCH --job-name=p58_runF
set -uo pipefail
P58=/data/gpfs/projects/punim2657/pota58_repro
P39=/data/gpfs/projects/punim2657/pota39_repro
SRC="${P39}/asm"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
ORIG="/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
MAIN=/data/gpfs/projects/punim2657/sfs_main
MSIF="${MAIN}/sfs_pristine_assembly.sif"
RUNDIR="${MAIN}/pota58_run_${SLURM_JOB_ID}"
BUN="${P58}/prep/pota58_bundle_F/SfS_pp"
BUNMD5="${P58}/prep/pota58_F_flagged_bun_md5.txt"
POT=F
STEPS=7
SHIM_HOST="${MAIN}/sfspreproc-docker/hpc/tools/main_pristine_batch.cpp"
GTSTUB_HOST="/data/gpfs/projects/punim2657/pota40_repro/gt_stub.cpp"
OVERLAY="${RUNDIR}.overlay_data_path.h"
echo "=== POTA-58 PILOT STAGE Pot_${POT} job ${SLURM_JOB_ID} ==="; date; hostname
[ "$(git -C "${SRC}" rev-parse HEAD)" = "bffefb6a983403ac45b96aa84a5c52f4fa0a814e" ] || { echo WRONG-ASM-HEAD; exit 1; }
git -C "${SRC}" status --porcelain | grep -v "^??" && { echo "ASM-DIFF-NONEMPTY"; exit 1; } || echo "asm tree clean"
[ "$(git -C "${SRC}" diff 9195c0167e2077a564bd7c91156063252feeb506..HEAD --name-only | tr '\n' ' ')" = "class/feature_matching.cpp class/ranking_system.cpp " ] || { echo "ASM-DELTA-WRONG-FILES"; exit 1; }
grep -q "P22FIX:" "${SRC}/class/feature_matching.cpp" || { echo "P22FIX-MISSING"; exit 1; }
grep -q "P22FIX2:" "${SRC}/class/ranking_system.cpp" || { echo "P22FIX2-MISSING"; exit 1; }
grep -q "axis_angle_ > 0.436" "${SRC}/class/feature_matching.cpp" || { echo "C2-GATE-NOT-0.436"; exit 1; }
grep -q "#define TOP_k 5" "${SHIM_HOST}" || { echo SHIM-K-NOT-5; exit 1; }
grep -q "#define BRANCH_b 3" "${SHIM_HOST}" || { echo SHIM-B-NOT-3; exit 1; }
echo "--- fresh bundle guard (must match flagged md5 record) ---"
md5sum "${BUN}/Breaklines"/*.pcd | sort > "${RUNDIR}.bun_md5_check.txt"
diff <(awk '{print $1}' "${BUNMD5}") <(awk '{print $1}' "${RUNDIR}.bun_md5_check.txt") && echo "F-BUNDLE-MATCHES-FLAGGED" || { echo "F-BUNDLE-DIFFERS"; exit 1; }
echo "--- overlay: POT_${POT} selector (untracked host file, clone untouched) ---"
sed -e 's|^#define POT_A$|//#define POT_A|' -e "s|^//#define POT_${POT}\$|#define POT_${POT}|" "${SRC}/class/data_path.h" > "${OVERLAY}"
diff "${SRC}/class/data_path.h" "${OVERLAY}"
[ "$(diff "${SRC}/class/data_path.h" "${OVERLAY}" | grep -c '^[<>]')" = "4" ] || { echo "OVERLAY-NOT-2-LINE-FLIP"; exit 1; }
grep -q "^#define POT_${POT}$" "${OVERLAY}" || { echo "OVERLAY-POT-NOT-ACTIVE"; exit 1; }
echo "overlay 2-line flip OK"
mkdir -p "${RUNDIR}"
build_and_run() { # $1=DS $2=ARM
  local DS="$1" ARM="$2"
  echo "===== CURE-${ARM} ====="
  mkdir -p "${RUNDIR}/${ARM}_Result"
  time "${APPTAINER}" exec --bind /data:/data --bind "${MAIN}:/workspace" --bind "${P39}:/p40" --bind "${OVERLAY}:/p40/asm/class/data_path.h" --bind "${DS}:/Dataset/SfS_pp" --bind "${RUNDIR}/${ARM}_Result:/Dataset/SfS_pp/Result" "${MSIF}" bash -c '
set -euo pipefail
RUNDIR="/workspace/pota58_run_'"${SLURM_JOB_ID}"'"
SRC="/p40/asm" ARM="'"${ARM}"'" POT="'"${POT}"'" STEPS="'"${STEPS}"'"
SHIM="/workspace/sfspreproc-docker/hpc/tools/main_pristine_batch.cpp"
GTSTUB="'"${GTSTUB_HOST}"'"
rm -rf /tmp/pb-p58-"${ARM}" && mkdir -p /tmp/pb-p58-"${ARM}" && cd /tmp/pb-p58-"${ARM}"
grep -q "P22FIX" "${SRC}/class/feature_matching.cpp" || { echo "P22FIX-MISSING-IN-CONTAINER"; exit 1; }
grep -q "P22FIX2" "${SRC}/class/ranking_system.cpp" || { echo "P22FIX2-MISSING-IN-CONTAINER"; exit 1; }
grep -q "^#define POT_'"${POT}"'$" "${SRC}/class/data_path.h" || { echo "OVERLAY-NOT-VISIBLE-IN-CONTAINER"; exit 1; }
grep -q "^//#define POT_A$" "${SRC}/class/data_path.h" || { echo "OVERLAY-POTA-STILL-ACTIVE"; exit 1; }
echo "OVERLAY-VISIBLE-IN-CONTAINER"
cmake "${SRC}" -DCMAKE_BUILD_TYPE=Release >"${RUNDIR}/${ARM}_cmake.log" 2>&1
make -j8 Hierarchy-Clear >"${RUNDIR}/${ARM}_make.log" 2>&1
D="CMakeFiles/Hierarchy-Clear.dir"
DEFS=$(grep "^CXX_DEFINES" $D/flags.make | cut -d= -f2- | tr " " "\n" | grep -v "GOOGLE_GLOG_DLL_DECL" | tr "\n" " " || true)
INCS=$(grep "^CXX_INCLUDES" $D/flags.make | cut -d= -f2- || true)
FLAGS=$(grep "^CXX_FLAGS" $D/flags.make | cut -d= -f2- || true)
SHIM_INC="-I${SRC} -I${SRC}/class"
g++ ${DEFS} ${INCS} ${FLAGS} ${SHIM_INC} -c "${SHIM}" -o CMakeFiles/shim.o
LINK=$(cat $D/link.txt)
LINK=${LINK//CMakeFiles\/Hierarchy-Clear.dir\/main.cpp.o/CMakeFiles\/shim.o}
LINK=${LINK//CMakeFiles\/Hierarchy-Clear.dir\/main_headless_correct.cpp.o/CMakeFiles\/shim.o}
LINK=${LINK//\/opt\/sfs-pristine\/build\/CMakeFiles\/Hierarchy-Clear.dir\/main.cpp.o/CMakeFiles\/shim.o}
case "${LINK}" in *shim.o*) echo "LINK-SHIM-OK";; *) echo "LINK-SHIM-MISS"; exit 1;; esac
case "${LINK}" in *main_headless_correct*) echo "LINK-FORKMAIN-LEAK"; exit 1;; *) echo "LINK-FORKMAIN-ABSENT-OK";; esac
OBJ=$(echo "${LINK}" | grep -o "[^ ]*shim\.o" | head -1)
[ -n "${OBJ}" ] && [ -f "${OBJ}" ] || { echo "SHIM-O-MISSING: ${OBJ}"; exit 1; }
echo "SHIM-O-FOUND: ${OBJ}"
LINK=${LINK/-o Hierarchy-Clear/-o Hierarchy-Batch-P58}
if eval "${LINK}" 2>"${RUNDIR}/${ARM}_link.err"; then echo "LINK-DONE-CLEAN"; else
  if grep -q "GroundTruthDebugger" "${RUNDIR}/${ARM}_link.err"; then
    echo "LINK-NEEDS-GT-STUB (ticket-38/40 contingency)"
    cp "'"${GTSTUB_HOST}"'" ./gt_stub_copy.cpp
    g++ ${DEFS} ${INCS} ${FLAGS} ${SHIM_INC} -c ./gt_stub_copy.cpp -o CMakeFiles/gt_stub.o
    LINK2="${LINK} CMakeFiles/gt_stub.o"
    LINK2=${LINK2/-o Hierarchy-Batch-P58/-o Hierarchy-Batch-P58}
    eval "${LINK2}" && echo "LINK-DONE-WITH-GT-STUB" || { echo "LINK-FAILED-EVEN-WITH-STUB"; exit 1; }
  else echo "LINK-FAILED-OTHER"; cat "${RUNDIR}/${ARM}_link.err"; exit 1; fi
fi
strings ./Hierarchy-Batch-P58 | grep -q "adaptive beam search TOP_k" && { echo "DRIVER-FORKMAIN-LEAK"; exit 1; } || echo "DRIVER-SHIM-OK"
mkdir -p /Dataset/SfS_pp/Result
time ./Hierarchy-Batch-P58 ${STEPS} >"${RUNDIR}/${ARM}_binary.log" 2>&1
rc=$?
grep -E "Total number|Sherd accuracy|Edge accuracy" "${RUNDIR}/${ARM}_binary.log" | tail -n 6 || true
mkdir -p "${RUNDIR}/${ARM}_Result_snapshot"
cp -pr /Dataset/SfS_pp/Result/. "${RUNDIR}/${ARM}_Result_snapshot/" 2>/dev/null || true
for rd in results_*/; do [ -d "$rd" ] && cp -pr "$rd" "${RUNDIR}/${ARM}_cwd_${rd%/}" || true; done
NT=$(ls "${RUNDIR}/${ARM}_Result_snapshot"/T_*.txt 2>/dev/null | wc -l)
echo "SNAPSHOT-T-COUNT=${NT}"
[ "${NT}" -gt 0 ] || { echo "SNAPSHOT-EMPTY-FAIL"; exit 1; }
rm -rf /Dataset/SfS_pp/Result
exit ${rc}
' > "${RUNDIR}/${ARM}_outer.log" 2>&1
  echo "CURE-${ARM} container exit $?"
}
build_and_run "${ORIG}" orig
build_and_run "${BUN}" fresh
echo "### tallies"; echo "--- orig ---"
grep -a -E "Total number|Sherd accuracy|Edge accuracy" "${RUNDIR}/orig_binary.log" | tail -4 || true
echo "--- fresh ---"
grep -a -E "Total number|Sherd accuracy|Edge accuracy" "${RUNDIR}/fresh_binary.log" | tail -4 || true
echo "### pruned counts"
grep -a -E "pruned|Pruned|Number of|hypothes" "${RUNDIR}/orig_binary.log" | tail -4 || true
grep -a -E "pruned|Pruned|Number of|hypothes" "${RUNDIR}/fresh_binary.log" | tail -4 || true
echo "### laptop fetch tarball"
FETCH="${RUNDIR}/pota58_fetch_F"
mkdir -p "${FETCH}/rims_fresh" "${FETCH}/GT"
cp -L "${BUN}/Breaklines"/Pot_F_Piece_*.pcd "${FETCH}/rims_fresh/"
cp -L "${BUN}/Ground Truth"/Pot_F_Piece_*_T.txt "${BUN}/Ground Truth"/Pot_F_simple_graph.txt "${FETCH}/GT/"
for ARM in orig fresh; do
  mkdir -p "${FETCH}/T_${ARM}"
  cp -L "${RUNDIR}/${ARM}_Result_snapshot"/T_*.txt "${FETCH}/T_${ARM}/" 2>/dev/null || true
  grep -a -E "Total number|Sherd accuracy|Edge accuracy" "${RUNDIR}/${ARM}_binary.log" | tail -4 > "${FETCH}/P58_${ARM}.txt" || true
done
tar -czf "${RUNDIR}/pota58_fetch_F.tgz" -C "${RUNDIR}" pota58_fetch_F
ls -la "${RUNDIR}"
date; echo POTA58-F-DONE
