#!/bin/bash
# POTA-176 STAGE: Pot C slot-exchange cure E2E (SXC C02+C04 Bl_0<->Bl_1 + S0<->S1;
# C01/C03 untouched byte-identical; zero ORIG points; prep-side scratch bundle copies only).
# Vehicle: cure-potA @ bffefb6 + k=5/b=3 shim (ticket-39/40/61 precedent).
# LINK-SHIM-OK + LINK-FORKMAIN-ABSENT-OK + DRIVER-SHIM-OK asserts per arm.
# 4 arms per job: A-orig + A-fresh (vehicle controls, STEPS=8) and
# C-orig (reference control) + C-176 (cure under test, STEPS=4).
# DS bundles are NEVER written: Result is bind-mounted to RUNDIR per arm.
# Overlay: host-side untracked data_path.h bind-mounted in-container only.
# Ticket 39-97 lanes read-only; this job writes only pota176_* paths.
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --time=12:00:00
#SBATCH --nodes=1 --ntasks-per-node=1 --cpus-per-task=8 --mem=32G
#SBATCH --job-name=p176_AC
set -uo pipefail
P176=/data/gpfs/projects/punim2657/pota176_repro
P39=/data/gpfs/projects/punim2657/pota39_repro
P40=/data/gpfs/projects/punim2657/pota40_repro
SRC="${P39}/asm"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
ORIG="/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
MAIN=/data/gpfs/projects/punim2657/sfs_main
MSIF="${MAIN}/sfs_pristine_assembly.sif"
RUNDIR="${MAIN}/pota176_run_${SLURM_JOB_ID}"
A_FRESH="${P40}/prep/pota40_bundle/SfS_pp"
A_FRESH_MD5="${P40}/prep/pota40_bun_md5.txt"
C_176="${P176}/prep/pota176_bundle_C_176/SfS_pp"
C_176_MD5="${P176}/pota176_C_176_BL_md5.txt"
SHIM_HOST="${MAIN}/sfspreproc-docker/hpc/tools/main_pristine_batch.cpp"
GTSTUB_HOST="${P40}/gt_stub.cpp"
echo "=== POTA-176 STAGE A+C job ${SLURM_JOB_ID} ==="; date; hostname
[ "$(git -C "${SRC}" rev-parse HEAD)" = "bffefb6a983403ac45b96aa84a5c52f4fa0a814e" ] || { echo WRONG-ASM-HEAD; exit 1; }
git -C "${SRC}" status --porcelain | grep -v "^??" && { echo "ASM-DIFF-NONEMPTY"; exit 1; } || echo "asm tree clean"
[ "$(git -C "${SRC}" diff 9195c0167e2077a564bd7c91156063252feeb506..HEAD --name-only | tr '\n' ' ')" = "class/feature_matching.cpp class/ranking_system.cpp " ] || { echo "ASM-DELTA-WRONG-FILES"; exit 1; }
grep -q "P22FIX" "${SRC}/class/feature_matching.cpp" || { echo "P22FIX-MISSING"; exit 1; }
grep -q "P22FIX2" "${SRC}/class/ranking_system.cpp" || { echo "P22FIX2-MISSING"; exit 1; }
grep -q "axis_angle_ > 0.436" "${SRC}/class/feature_matching.cpp" || { echo "C2-GATE-NOT-0.436"; exit 1; }
grep -riq "FACE VETO\|face_veto" "${SRC}/class/" && { echo VETO-PRESENT-STOP; exit 1; } || echo "VETO-ABSENT-OK"
grep -q "#define TOP_k 5" "${SHIM_HOST}" || { echo SHIM-K-NOT-5; exit 1; }
grep -q "#define BRANCH_b 3" "${SHIM_HOST}" || { echo SHIM-B-NOT-3; exit 1; }
echo "--- bundle guards (read-only; md5 proves no other-ticket writes) ---"
(cd "${A_FRESH}/Breaklines" && md5sum -c "${A_FRESH_MD5}" | grep -v ": OK" && { echo "A-FRESH-BUNDLE-CHANGED"; exit 1; }) || echo "A-fresh bundle intact"
(cd "${C_176}/Breaklines" && md5sum -c "${C_176_MD5}" | grep -v ": OK" && { echo "C-176-BUNDLE-CHANGED"; exit 1; }) || echo "C-176 bundle intact"
make_overlay() {
  local POT="$1" OV="${RUNDIR}.overlay_data_path_${1}.h"
  if [ "${POT}" = "A" ]; then cp "${SRC}/class/data_path.h" "${OV}"; echo "${OV}"; return; fi
  sed -e 's|^#define POT_A$|//#define POT_A|' -e "s|^//[ ]*#define POT_${POT}\$|#define POT_${POT}|" "${SRC}/class/data_path.h" > "${OV}"
  [ "$(diff "${SRC}/class/data_path.h" "${OV}" | grep -c '^[<>]')" = "4" ] || { echo "OVERLAY-${POT}-NOT-2-LINE-FLIP"; exit 1; }
  grep -q "^#define POT_${POT}$" "${OV}" || { echo "OVERLAY-${POT}-NOT-ACTIVE"; exit 1; }
  echo "${OV}"
}
mkdir -p "${RUNDIR}"
OV_A="$(make_overlay A)"
OV_C="$(make_overlay C)"
echo "overlays OK"
build_and_run() {
  local POT="$1" DS="$2" ARM="$3" STEPS="$4" OVERLAY="$5"
  echo "===== CURE-${ARM} (POT_${POT} STEPS=${STEPS}) ====="
  mkdir -p "${RUNDIR}/${ARM}_Result"
  time "${APPTAINER}" exec --bind /data:/data --bind "${MAIN}:/workspace" --bind "${P39}:/p40" --bind "${OVERLAY}:/p40/asm/class/data_path.h" --bind "${DS}:/Dataset/SfS_pp" --bind "${RUNDIR}/${ARM}_Result:/Dataset/SfS_pp/Result" "${MSIF}" bash -c '
set -euo pipefail
RUNDIR="/workspace/pota176_run_'"${SLURM_JOB_ID}"'"
SRC="/p40/asm" ARM="'"${ARM}"'" POT="'"${POT}"'" STEPS="'"${STEPS}"'"
SHIM="/workspace/sfspreproc-docker/hpc/tools/main_pristine_batch.cpp"
GTSTUB="'"${GTSTUB_HOST}"'"
rm -rf /tmp/pb-p176-'"${SLURM_JOB_ID}"'-"${ARM}" && mkdir -p /tmp/pb-p176-'"${SLURM_JOB_ID}"'-"${ARM}" && cd /tmp/pb-p176-'"${SLURM_JOB_ID}"'-"${ARM}"
grep -q "P22FIX" "${SRC}/class/feature_matching.cpp" || { echo "P22FIX-MISSING-IN-CONTAINER"; exit 1; }
grep -q "P22FIX2" "${SRC}/class/ranking_system.cpp" || { echo "P22FIX2-MISSING-IN-CONTAINER"; exit 1; }
grep -riq "FACE VETO\|face_veto" "${SRC}/class/" && { echo VETO-PRESENT-IN-CONTAINER-STOP; exit 1; } || echo "VETO-ABSENT-IN-CONTAINER-OK"
grep -q "^#define POT_'"${POT}"'$" "${SRC}/class/data_path.h" || { echo "OVERLAY-NOT-VISIBLE-IN-CONTAINER"; exit 1; }
echo "OVERLAY-POT-'"${POT}"'-VISIBLE"
grep -q "#define TOP_k 5" "${SHIM}" || { echo SHIM-K-NOT-5-IN-CONTAINER; exit 1; }
grep -q "#define BRANCH_b 3" "${SHIM}" || { echo SHIM-B-NOT-3-IN-CONTAINER; exit 1; }
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
LINK=${LINK/-o Hierarchy-Clear/-o Hierarchy-Batch-P176}
if eval "${LINK}" 2>"${RUNDIR}/${ARM}_link.err"; then echo "LINK-DONE-CLEAN"; else
  if grep -q "GroundTruthDebugger" "${RUNDIR}/${ARM}_link.err"; then
    echo "LINK-NEEDS-GT-STUB (ticket-38/40 contingency)"
    cp "'"${GTSTUB_HOST}"'" ./gt_stub_copy.cpp
    g++ ${DEFS} ${INCS} ${FLAGS} ${SHIM_INC} -c ./gt_stub_copy.cpp -o CMakeFiles/gt_stub.o
    LINK2="${LINK} CMakeFiles/gt_stub.o"
    LINK2=${LINK2/-o Hierarchy-Batch-P176/-o Hierarchy-Batch-P176}
    eval "${LINK2}" && echo "LINK-DONE-WITH-GT-STUB" || { echo "LINK-FAILED-EVEN-WITH-STUB"; exit 1; }
  else echo "LINK-FAILED-OTHER"; cat "${RUNDIR}/${ARM}_link.err"; exit 1; fi
fi
strings ./Hierarchy-Batch-P176 | grep -q "adaptive beam search TOP_k" && { echo "DRIVER-FORKMAIN-LEAK"; exit 1; } || echo "DRIVER-SHIM-OK"
time ./Hierarchy-Batch-P176 ${STEPS} >"${RUNDIR}/${ARM}_binary.log" 2>&1
rc=$?
grep -E "Total number|Sherd accuracy|Edge accuracy" "${RUNDIR}/${ARM}_binary.log" | tail -n 6 || true
mkdir -p "${RUNDIR}/${ARM}_Result_snapshot"
cp -pr /Dataset/SfS_pp/Result/. "${RUNDIR}/${ARM}_Result_snapshot/" 2>/dev/null || true
for rd in results_*/; do [ -d "$rd" ] && cp -pr "$rd" "${RUNDIR}/${ARM}_cwd_${rd%/}" || true; done
NT=$(ls "${RUNDIR}/${ARM}_Result_snapshot"/T_*.txt 2>/dev/null | wc -l)
echo "SNAPSHOT-T-COUNT=${NT}"
[ "${NT}" -gt 0 ] || { echo "SNAPSHOT-EMPTY-FAIL"; exit 1; }
exit ${rc}
' > "${RUNDIR}/${ARM}_outer.log" 2>&1
  echo "CURE-${ARM} container exit $?"
}
build_and_run A "${ORIG}" A_orig 8 "${OV_A}"
build_and_run A "${A_FRESH}" A_fresh 8 "${OV_A}"
build_and_run C "${ORIG}" C_orig 4 "${OV_C}"
build_and_run C "${C_176}" C_176 4 "${OV_C}"
echo "### tallies"
for ARM in A_orig A_fresh C_orig C_176; do
  echo "--- ${ARM} ---"
  grep -a -E "Total number|Sherd accuracy|Edge accuracy" "${RUNDIR}/${ARM}_binary.log" | tail -4 || true
done
echo "### pruned counts"
for ARM in A_orig A_fresh C_orig C_176; do
  echo "--- ${ARM} ---"
  grep -a -E "pruned|Pruned|Number of|hypothes" "${RUNDIR}/${ARM}_binary.log" | tail -3 || true
done
echo "### asserts"
grep -h -E "LINK-SHIM-OK|LINK-FORKMAIN-ABSENT-OK|DRIVER-SHIM-OK" "${RUNDIR}"/*_outer.log | sort | uniq -c
echo "### laptop fetch tarball"
FETCH="${RUNDIR}/pota176_fetch"
mkdir -p "${FETCH}/rims_C176" "${FETCH}/GT_C"
cp -L "${C_176}/Breaklines"/Pot_C_Piece_*.pcd "${FETCH}/rims_C176/"
cp -L "${C_176}/Ground Truth"/Pot_C_Piece_*_T.txt "${C_176}/Ground Truth"/Pot_C_simple_graph.txt "${FETCH}/GT_C/"
for ARM in A_orig A_fresh C_orig C_176; do
  mkdir -p "${FETCH}/T_${ARM}"
  cp -L "${RUNDIR}/${ARM}_Result_snapshot"/T_*.txt "${FETCH}/T_${ARM}/" 2>/dev/null || true
  grep -a -E "Total number|Sherd accuracy|Edge accuracy" "${RUNDIR}/${ARM}_binary.log" | tail -4 > "${FETCH}/P176_${ARM}.txt" || true
done
tar -czf "${RUNDIR}/pota176_fetch.tgz" -C "${RUNDIR}" pota176_fetch
ls -la "${RUNDIR}"
date; echo POTA176-AC-DONE
