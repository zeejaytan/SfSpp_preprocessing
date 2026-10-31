#!/bin/bash
# POTA-204 STAGE: PRISTINE Pot C E2E (D-all: 4x TRUE thin-loop Bl_0 C01-C04 on PRISTINE fresh
# base; all other slots byte-identical to pristine base; zero ORIG points).
# Vehicle: PRISTINE asm @ 11f4827 (sections A+B+C ALL OUT) + k=5/b=3 in-tree shim.
# 5 arms per job: A-orig + A-fresh (vehicle controls, STEPS=8), C-orig (THE BAR,
# pristine+ORIG, STEPS=4) + C-fresh (pristine+fresh-unchained, STEPS=4) + C-204
# (pristine+D under test, STEPS=4).
# LINK-SHIM-OK + LINK-FORKMAIN-ABSENT-OK + DRIVER-SHIM-OK asserts per arm.
# DS bundles are NEVER written: Result is bind-mounted to RUNDIR per arm.
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --time=12:00:00
#SBATCH --nodes=1 --ntasks-per-node=1 --cpus-per-task=8 --mem=32G
#SBATCH --job-name=p204_AC
set -uo pipefail
P204=/data/gpfs/projects/punim2657/pota204_repro
P40=/data/gpfs/projects/punim2657/pota40_repro
SRC="${P204}/pota204_asm"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
ORIG="/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
MAIN=/data/gpfs/projects/punim2657/sfs_main
MSIF="${MAIN}/sfs_pristine_assembly.sif"
RUNDIR="${MAIN}/pota204_run_${SLURM_JOB_ID}"
A_FRESH="${P40}/prep/pota40_bundle/SfS_pp"
A_FRESH_MD5="${P40}/prep/pota40_bun_md5.txt"
C_FRESH="/data/gpfs/projects/punim2657/pota197_repro/pota197_prep/pota197_bundle_C/SfS_pp"
C_FRESH_MD5="/data/gpfs/projects/punim2657/pota197_repro/pota197_prep/pota197_C_bun_md5.txt"
C_204="${P204}/prep/pota204_bundle_C_204/SfS_pp"
C_204_MD5="${P204}/pota204_C_204_BL_md5.txt"
SHIM_HOST="${SRC}/hpc/tools/main_pristine_batch.cpp"
GTSTUB_HOST="${P40}/gt_stub.cpp"
echo "=== POTA-204 PRISTINE STAGE A+C job ${SLURM_JOB_ID} ==="; date; hostname
[ "$(git -C "${SRC}" rev-parse HEAD)" = "$(git -C "${SRC}" rev-parse 11f4827)" ] || { echo WRONG-ASM-HEAD; exit 1; }
git -C "${SRC}" status --porcelain | grep -v "^??" && { echo "ASM-DIFF-NONEMPTY"; exit 1; } || echo "asm tree clean"
[ -z "$(git -C "${SRC}" diff 11f4827..HEAD --name-only)" ] || { echo "ASM-DELTA-NONEMPTY"; exit 1; }
grep -q "P22FIX" "${SRC}/class/feature_matching.cpp" "${SRC}/class/ranking_system.cpp" && { echo P22FIX-PRESENT-STOP; exit 1; } || echo "P22FIX-ABSENT-OK"
grep -q "(iter->score_ > 10) || (iter->overlap_)" "${SRC}/class/feature_matching.cpp" || { echo VETO-GONE-WRONG; exit 1; }
grep -q "axis_angle_ > 0.436" "${SRC}/class/feature_matching.cpp" && { echo C2-PRESENT-STOP; exit 1; } || echo "C2-ABSENT-OK"
grep -q "axis_angle_ > 0.610" "${SRC}/class/feature_matching.cpp" || { echo GATE-NOT-0.610; exit 1; }
grep -q "50); // PAPER-CONFIG" "${SRC}/class/ranking_system.cpp" || { echo RANK-NOT-50; exit 1; }
grep -riq "FACE VETO\|face_veto" "${SRC}/class/" && { echo VETO-PRESENT-STOP; exit 1; } || echo "VETO-ABSENT-OK"
grep -q "#define TOP_k 5" "${SHIM_HOST}" || { echo SHIM-K-NOT-5; exit 1; }
grep -q "#define BRANCH_b 3" "${SHIM_HOST}" || { echo SHIM-B-NOT-3; exit 1; }
echo "pristine vehicle markers ALL-OK (A/B/C out, gate 0.610, rank 50, k5/b3)"
echo "--- bundle guards (read-only) ---"
(cd "${A_FRESH}/Breaklines" && md5sum -c "${A_FRESH_MD5}" | grep -v ": OK" && { echo "A-FRESH-BUNDLE-CHANGED"; exit 1; }) || echo "A-fresh bundle intact"
(cd "${C_FRESH}/Breaklines" && md5sum -c "${C_FRESH_MD5}" | grep -v ": OK" && { echo "C-FRESH-BUNDLE-CHANGED"; exit 1; }) || echo "C-fresh (pristine base) intact"
(cd "${C_204}/Breaklines" && md5sum -c "${C_204_MD5}" | grep -v ": OK" && { echo "C-204-BUNDLE-CHANGED"; exit 1; }) || echo "C-204 bundle intact"
make_overlay() {
  local POT="$1" OV="${RUNDIR}.overlay_data_path_${1}.h"
  if [ "${POT}" = "A" ]; then cp "${SRC}/class/data_path.h" "${OV}"; echo "${OV}"; return; fi
  sed -e 's|^#define POT_A|//#define POT_A|' -e "s|^//[ ]*#define POT_${POT}\$|#define POT_${POT}|" "${SRC}/class/data_path.h" > "${OV}"
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
  echo "===== LOOP-${ARM} (POT_${POT} STEPS=${STEPS}) ====="
  mkdir -p "${RUNDIR}/${ARM}_Result"
  time "${APPTAINER}" exec --bind /data:/data --bind "${MAIN}:/workspace" --bind "${P204}:/p204" --bind "${OVERLAY}:/p204/pota204_asm/class/data_path.h" --bind "${DS}:/Dataset/SfS_pp" --bind "${RUNDIR}/${ARM}_Result:/Dataset/SfS_pp/Result" "${MSIF}" bash -c '
set -euo pipefail
RUNDIR="/workspace/pota204_run_'"${SLURM_JOB_ID}"'"
SRC="/p204/pota204_asm" ARM="'"${ARM}"'" POT="'"${POT}"'" STEPS="'"${STEPS}"'"
SHIM="/p204/pota204_asm/hpc/tools/main_pristine_batch.cpp"
GTSTUB="'"${GTSTUB_HOST}"'"
rm -rf /tmp/pb-p204-'"${SLURM_JOB_ID}"'"-${ARM}" && mkdir -p /tmp/pb-p204-'"${SLURM_JOB_ID}"'"-${ARM}" && cd /tmp/pb-p204-'"${SLURM_JOB_ID}"'"-${ARM}"
grep -q "P22FIX" "${SRC}/class/feature_matching.cpp" "${SRC}/class/ranking_system.cpp" && { echo P22FIX-PRESENT-IN-CONTAINER-STOP; exit 1; } || echo "P22FIX-ABSENT-IN-CONTAINER-OK"
grep -q "axis_angle_ > 0.610" "${SRC}/class/feature_matching.cpp" || { echo GATE-NOT-0.610-IN-CONTAINER; exit 1; }
grep -q "50); // PAPER-CONFIG" "${SRC}/class/ranking_system.cpp" || { echo RANK-NOT-50-IN-CONTAINER; exit 1; }
grep -riq "FACE VETO\|face_veto" "${SRC}/class/" && { echo VETO-PRESENT-IN-CONTAINER-STOP; exit 1; } || echo "VETO-ABSENT-IN-CONTAINER-OK"
grep -Eq "^#define POT_'"${POT}"'([^_]|$)" "${SRC}/class/data_path.h" || { echo "OVERLAY-NOT-VISIBLE-IN-CONTAINER"; exit 1; }
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
LINK=${LINK/-o Hierarchy-Clear/-o Hierarchy-Batch-P204}
if eval "${LINK}" 2>"${RUNDIR}/${ARM}_link.err"; then echo "LINK-DONE-CLEAN";
else
  if grep -q "GroundTruthDebugger" "${RUNDIR}/${ARM}_link.err"; then
    echo "LINK-NEEDS-GT-STUB (38/40 contingency; build scaffolding, not a cure)"
    cp "'"${GTSTUB_HOST}"'" ./gt_stub_copy.cpp
    g++ ${DEFS} ${INCS} ${FLAGS} ${SHIM_INC} -c ./gt_stub_copy.cpp -o CMakeFiles/gt_stub.o
    LINK2="${LINK} CMakeFiles/gt_stub.o"
    LINK2=${LINK2/-o Hierarchy-Batch-P204/-o Hierarchy-Batch-P204}
    eval "${LINK2}" && echo "LINK-DONE-WITH-GT-STUB" || { echo "LINK-FAILED-EVEN-WITH-STUB"; exit 1; }
  else echo "LINK-FAILED-OTHER"; cat "${RUNDIR}/${ARM}_link.err"; exit 1; fi
fi
strings ./Hierarchy-Batch-P204 | grep -q "adaptive beam search TOP_k" && { echo "DRIVER-FORKMAIN-LEAK"; exit 1; } || echo "DRIVER-SHIM-OK"
time ./Hierarchy-Batch-P204 ${STEPS} >"${RUNDIR}/${ARM}_binary.log" 2>&1
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
  echo "LOOP-${ARM} container exit $?"
}
build_and_run A "${ORIG}" A_orig 8 "${OV_A}"
build_and_run A "${A_FRESH}" A_fresh 8 "${OV_A}"
build_and_run C "${ORIG}" C_orig 4 "${OV_C}"
build_and_run C "${C_FRESH}" C_fresh 4 "${OV_C}"
build_and_run C "${C_204}" C_204 4 "${OV_C}"
echo "### tallies"
for ARM in A_orig A_fresh C_orig C_fresh C_204; do
  echo "--- ${ARM} ---"
  grep -a -E "Total number|Sherd accuracy|Edge accuracy" "${RUNDIR}/${ARM}_binary.log" | tail -4 || true
done
echo "### pruned counts"
for ARM in A_orig A_fresh C_orig C_fresh C_204; do
  echo "--- ${ARM} ---"
  grep -a -E "pruned|Pruned|Number of|hypothes" "${RUNDIR}/${ARM}_binary.log" | tail -3 || true
done
echo "### asserts"
grep -h -E "LINK-SHIM-OK|LINK-FORKMAIN-ABSENT-OK|DRIVER-SHIM-OK" "${RUNDIR}"/*_outer.log | sort | uniq -c
echo "### laptop fetch tarball"
FETCH="${RUNDIR}/pota204_fetch"
mkdir -p "${FETCH}/rims_C197" "${FETCH}/GT_C"
cp -L "${C_204}/Breaklines"/Pot_C_Piece_*.pcd "${FETCH}/rims_C204/"
cp -L "${C_204}/Ground Truth"/Pot_C_Piece_*_T.txt "${C_204}/Ground Truth"/Pot_C_simple_graph.txt "${FETCH}/GT_C/"
for ARM in A_orig A_fresh C_orig C_fresh C_204; do
  mkdir -p "${FETCH}/T_${ARM}"
  cp -L "${RUNDIR}/${ARM}_Result_snapshot"/T_*.txt "${FETCH}/T_${ARM}/" 2>/dev/null || true
done
date; echo P204-STAGE-DONE
