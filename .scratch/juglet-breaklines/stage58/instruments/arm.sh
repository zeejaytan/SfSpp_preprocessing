#!/bin/bash
# arm.sh -- ticket 58: ONE panel arm, executed INSIDE the sfs_pristine_assembly.sif container.
# The caller (run_panel_t58.sbatch) binds, for EACH arm:
#   $MAIN  -> /workspace      (the sfspreproc-docker checkout carrying the shim source)
#   $WORK  -> /panel          (build tree, include roots, shim variants, logs)
#   $OUT   -> /out            (per-arm Result snapshots)
#   $TREE  -> /Dataset/SfS_pp (the staged input tree this arm reads; Result/ lands inside it)
# and calls:  bash /panel/arm.sh ARM FLOOR INCDIR NP EXTRA
#   ARM    label (F50/F45/F10/F0/I60/F10R/PA10)
#   FLOOR  the lane-dot floor sed-ed into the gate (main_pristine_batch.cpp:86)
#   INCDIR /panel/inc1 (JUGLET_ORIG block appended, POT_A renamed off) or /panel/inc2 (stock)
#   NP     argument to the binary (shard count: 9 Juglet / 8 Pot A)
#   EXTRA  -DJUGLET_ORIG for Juglet arms, the literal NONE for Pot A
# The experimental binary is NEVER merged: it is compiled from a sed-ed COPY kept in /panel/shim.
set -uo pipefail
ARM=$1; FLOOR=$2; INC=$3; NP=$4; EXTRA=$5
if [ "$EXTRA" = "NONE" ]; then EXTRA=""; fi

BUILD=/panel/build
D=$BUILD/CMakeFiles/Hierarchy-Clear.dir
SHIM_SRC=/workspace/sfspreproc-docker/hpc/tools/main_pristine_batch.cpp
mkdir -p /panel/logs /panel/shim /out/$ARM

echo "########## arm $ARM floor=$FLOOR np=$NP extra=[$EXTRA] $(date -u +%FT%TZ)"
echo "--- hostname: $(hostname)"
echo "--- shim source md5: $(md5sum $SHIM_SRC | cut -d" " -f1)"
echo "--- include root: $INC"
grep -n "^#define POT_A\|^#define POT_A_INFRA\|^#define JUGLET_ORIG_BASE" $INC/class/data_path.h || true
echo "--- bound input tree /Dataset/SfS_pp:"
ls /Dataset/SfS_pp || true
echo "--- lane files this arm will read (md5 + dots):"
for f in /Dataset/SfS_pp/Breaklines/*.pcd; do
  n=$(awk "f{print} /^DATA/{f=1}" "$f" | grep -c . || true)
  echo "    $(basename $f) md5=$(md5sum $f | cut -d" " -f1) dots=$n"
done

if [ ! -f $BUILD/CMakeCache.txt ]; then
  echo "--- pristine objects: cold build"
  mkdir -p $BUILD
  cd $BUILD
  cmake /opt/sfs-pristine -DCMAKE_BUILD_TYPE=Release > /panel/logs/cmake.log 2>&1
  make -j8 > /panel/logs/make.log 2>&1
  echo "--- pristine objects built rc=$?"
else
  echo "--- pristine objects: reusing $BUILD"
fi
cd $BUILD
cat $D/flags.make > /panel/logs/flags_$ARM.log

# ---- the experimental variant: sed the floor on a COPY, keep md5 + diff ----------
VAR=/panel/shim/$ARM.cpp
sed "s/point_\.cols() < 50/point_.cols() < $FLOOR/" $SHIM_SRC > $VAR
if ! grep -q "point_.cols() < $FLOOR" $VAR; then
  echo "!!!! SED DID NOT APPLY for floor $FLOOR"; exit 3
fi
echo "--- variant md5: $(md5sum $VAR | cut -d" " -f1)"
diff -u $SHIM_SRC $VAR > /panel/logs/diff_$ARM.txt || true
echo "--- diff vs the shipped shim (expect exactly the floor literal):"
cat /panel/logs/diff_$ARM.txt

DEFS=$(grep "^CXX_DEFINES" $D/flags.make | cut -d= -f2- | tr " " "\n" | grep -v GOOGLE_GLOG_DLL_DECL | tr "\n" " ")
INCS=$(grep "^CXX_INCLUDES" $D/flags.make | cut -d= -f2-)
FLAGS=$(grep "^CXX_FLAGS" $D/flags.make | cut -d= -f2-)
g++ -I$INC $EXTRA $DEFS $INCS $FLAGS -I/opt/sfs-pristine -I/opt/sfs-pristine/class -c $VAR -o $D/shim_$ARM.o
echo "--- compile rc=$?"

cat $D/link.txt > /panel/logs/link_raw_$ARM.txt
LINK=$(sed -e "s|CMakeFiles/Hierarchy-Clear.dir/main.cpp.o|CMakeFiles/Hierarchy-Clear.dir/shim_$ARM.o|" -e "s|/opt/sfs-pristine/build/CMakeFiles/Hierarchy-Clear.dir/main.cpp.o|CMakeFiles/Hierarchy-Clear.dir/shim_$ARM.o|" -e "s|-o Hierarchy-Clear|-o Hierarchy-$ARM|" /panel/logs/link_raw_$ARM.txt)
echo "$LINK" > /panel/logs/link_$ARM.txt
eval "$LINK"
echo "--- link rc=$?"
ls -lh Hierarchy-$ARM

# ---- run ------------------------------------------------------------------------
rm -rf /Dataset/SfS_pp/Result
mkdir -p /Dataset/SfS_pp/Result
t0=$SECONDS
./Hierarchy-$ARM $NP > /panel/logs/binary_$ARM.log 2>&1
rc=$?
dt=$((SECONDS - t0))
echo "--- batch exit=$rc wall=${dt}s"
grep -E "Total number|Sherd accuracy|Edge accuracy|Result save finish|Saving transformation|co-first|End condition|Node Sequence|Rank|segmentation" /panel/logs/binary_$ARM.log | tail -14 || true
ls -la --time-style=full-iso /Dataset/SfS_pp/Result/ > /panel/logs/result_ls_$ARM.log || true
cp -pr /Dataset/SfS_pp/Result/. /out/$ARM/ 2>/dev/null || true
rm -rf /Dataset/SfS_pp/Result
echo "--- snapshot in /out/$ARM:"
ls /out/$ARM | head -20
echo "########## arm $ARM done rc=$rc wall=${dt}s"
exit $rc
