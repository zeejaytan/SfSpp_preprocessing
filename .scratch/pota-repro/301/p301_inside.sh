#!/usr/bin/env bash
# Ticket 301 -- runs INSIDE sfs_pristine_assembly.sif (adapted from ticket 298's p298_inside.sh).
# The pinned assembler (upstream 9195c016) is GUI-only and segfaults under Xvfb, so the batch shim
# hpc/tools/main_pristine_batch.cpp is compiled out-of-source against the pinned tree and linked with
# its objects: upstream main.cpp with viewer statements removed, nothing else.
#   * the pot is a #define in class/data_path.h, so the selector is flipped in a THROWAWAY COPY of the
#     pinned tree in /tmp (the pinned tree is read-only and is never touched);
#   * the bundle is whatever is bind-mounted at /Dataset/SfS_pp.
# Both are configuration. No algorithm, threshold, weight or ordering is changed anywhere.
# Ticket 301 adds one thing and changes nothing else: before the build it records what the CONTAINER
# sees on the target piece's axis path, so the swap can be proved to sit where the loader reads.
set -euo pipefail
R=/p301run
: ${POT:?} ; : ${SHARD:?} ; : ${ARM:?}
TARGET=${TARGET:-}
POTSEL=$(echo "POT_${POT#Pot_}" | tr 'a-z' 'A-Z')
BD=$(mktemp -d /tmp/p301-build-XXXXXX) && cd "$BD"
echo "[P301] build dir $BD (fresh; /tmp is shared between jobs on a node, never reuse a name)"
echo "[P301] inside $(hostname); pot=$POT arm=$ARM shard=$SHARD target=${TARGET:-none}"

# ------------------------------------------------ what the container sees on the target axis path
md5sum /Dataset/SfS_pp/Axes/*.xyz | sort -k2 > "$R/out/axes_seen_in_container.md5"
echo "[P301] axes visible to the loader: $(wc -l < "$R/out/axes_seen_in_container.md5")"
if [ -n "$TARGET" ]; then
  TA=/Dataset/SfS_pp/Axes/${TARGET}_Axis.xyz
  {
    echo "target ${TARGET}"
    echo "path $TA"
    echo "is_symlink $([ -L "$TA" ] && echo yes || echo no)"
    echo "resolves_to $(readlink -f "$TA")"
    echo "size_bytes $(stat -c %s "$TA")"
    echo "md5 $(md5sum "$TA" | awk '{print $1}')"
    echo "lines $(grep -c . "$TA")"
    echo "--- content as the container sees it ---"
    cat "$TA"
  } | tee "$R/out/target_axis_seen_in_container.txt"
fi

cp -a /opt/sfs-pristine "$BD/sfx"
H="$BD/sfx/class/data_path.h"
echo "[P301] pinned header md5 (before flip) $(md5sum "$H" | awk '{print $1}')"
sed -i -E "s|^#define (POT_[A-Z_]+)[[:space:]]*\$|//#define \1|" "$H"
sed -i -E "s|^// ?#define (${POTSEL})[[:space:]]*\$|#define \1|" "$H"
ACTIVE=$(grep -c "^#define POT_" "$H" || true)
if [ "${ACTIVE:-0}" != "1" ] || ! grep -q "^#define ${POTSEL}\$" "$H"; then
  echo "[P301] FATAL selector flip failed: $(grep -n '^#define POT_' "$H" || echo none) active"
  grep -n "define POT_" "$H" | head -20
  exit 20
fi
BLOCK=$(grep -m1 -n "^#ifdef ${POTSEL}\$" "$H" | cut -d: -f1 || true)
if [ -z "$BLOCK" ]; then echo "[P301] FATAL no #ifdef ${POTSEL} block in the header"; exit 22; fi
# one reader, no pipe: sed | grep -m1 makes sed die of SIGPIPE and pipefail turns that into a
# silent abort under set -e (cost ticket 298 two pilot attempts).
BLOCK_SHARD=$(awk -v s="$BLOCK" 'NR>=s && !f && /^#define SHARD_NUMBER/ {print $3; f=1}' "$H")
if [ "${BLOCK_SHARD:-x}" != "${SHARD}" ]; then
  echo "[P301] FATAL SHARD_NUMBER of $POT is ${BLOCK_SHARD:-absent}, job was given $SHARD"
  exit 21
fi
{
  echo "pot $POT"
  echo "selector $POTSEL"
  echo "selector line $(grep -n "^#define ${POTSEL}\$" "$H" | cut -d: -f1)"
  echo "ifdef line $BLOCK"
  echo "SHARD_NUMBER $BLOCK_SHARD"
  echo "header md5 after flip $(md5sum "$H" | awk '{print $1}')"
} | tee "$R/out/selector.txt"

mkdir -p "$BD/build" && cd "$BD/build"
cmake "$BD/sfx" -DCMAKE_BUILD_TYPE=Release > "$R/logs/shim_cmake.log" 2>&1
make -j8 > "$R/logs/shim_make.log" 2>&1
echo "[P301] pristine objects built: $(ls CMakeFiles/Hierarchy-Clear.dir/*.o 2>/dev/null | wc -l)"
D=CMakeFiles/Hierarchy-Clear.dir
DEFS=$(grep "^CXX_DEFINES" $D/flags.make | cut -d= -f2- | tr " " "\n" | grep -v "GOOGLE_GLOG_DLL_DECL" | tr "\n" " ")
INCS=$(grep "^CXX_INCLUDES" $D/flags.make | cut -d= -f2-)
FLAGS=$(grep "^CXX_FLAGS" $D/flags.make | cut -d= -f2-)
g++ ${DEFS} ${INCS} ${FLAGS} -I"$BD/sfx" -I"$BD/sfx/class" \
    -c /workspace/hpc/tools/main_pristine_batch.cpp -o CMakeFiles/shim.o
LINK=$(cat $D/link.txt)
LINK=${LINK//CMakeFiles\/Hierarchy-Clear.dir\/main.cpp.o/CMakeFiles\/shim.o}
LINK=${LINK//\/opt\/sfs-pristine\/build\/CMakeFiles\/Hierarchy-Clear.dir\/main.cpp.o/CMakeFiles\/shim.o}
LINK=${LINK/-o Hierarchy-Clear/-o Hierarchy-Batch}
echo "$LINK" > "$R/logs/shim_link.txt"
eval "$LINK"
ls -l Hierarchy-Batch | tee "$R/logs/binary_ls.txt"
md5sum Hierarchy-Batch | tee "$R/logs/binary.md5"

set +e
time ./Hierarchy-Batch "$SHARD" > "$R/logs/assembly.log" 2>&1
RC=$?
set -e
echo "assembly exit $RC" > "$R/out/assembly_exit.txt"
echo "[P301] assembly exit $RC"
grep -E "Total number|Sherd accuracy|Edge accuracy|Result save finish|Saving transformation|co-first" \
    "$R/logs/assembly.log" | tail -n 12 | tee "$R/out/summary.txt" || true
ls -la /Dataset/SfS_pp/Result/ > "$R/out/result_ls.txt" 2>&1 || true
cd / && rm -rf "$BD"
exit 0
