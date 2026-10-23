#!/usr/bin/env bash
#
# build.sh -- the ONE build entry point for SfSpp_preprocessing.
#
#   ./build.sh --target nurbs|mesh|axis [--variant NAME] [--build-dir DIR]
#              [--container PATH] [--jobs N] [--dry-run]
#
# WHY THIS EXISTS
# The repo root holds 33 build_*.sh scripts. They vary along one real axis (which
# pre-provisioned Apptainer image has a usable PCL/CGAL) and one fake one (which
# targets to compile), yet each is a full copy -- and the copy habit is what
# produced the tracked-file rewrite: build_enhanced_2024_final.sh opens with
# 'cat > CMakeLists.txt', so after a build the working tree is dirty and the
# source tree no longer describes the source. Only 8 of the 33 compile against an
# existing image, and those 8 differ only in image, source root, cmake -D and make
# target. That is the whole variation this file parameterises.
#
# WHAT IT GUARANTEES
#   1. It never writes into the source tree. Every artifact lands in
#      build/<target>-<variant>/ inside the worktree it is run from; the repo root
#      is discovered from this file's own location, never hardcoded, so a worktree
#      builds itself and not the main checkout.
#   2. It never rewrites a tracked file, and it proves that at the end: git status
#      is captured before and after, and a difference is a hard failure (exit 3),
#      not a warning.
#   3. The compiler runs inside the container, as every legacy script did:
#      apptainer exec --bind /data:/data <sif> bash -c "cmake -S .. -B .. && make .."
#
# WHAT IT DOES NOT DO
# It does not retire the 33 legacy scripts; proving this script correct comes
# first. docs/notes/build.md maps legacy script -> build.sh invocation and says
# which ones it deliberately does not replace (image provisioning, one-off
# experiment programs).
#
set -euo pipefail

APPTAINER="${APPTAINER:-/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer}"

# Repo root = the directory holding this script. Deliberately NOT the legacy
# ROOT=/data/gpfs/projects/punim2657/sfs_preprocessing: that constant is why the
# old scripts could only ever build one checkout, and why building in a worktree
# meant hand-editing the script.
REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"

TARGETS=()
VARIANT=default
BUILD_DIR=""
CONTAINER=""
JOBS=""
DRY_RUN=0

die() { printf 'build.sh: error: %s\n' "$*" >&2; exit 1; }
say() { printf '%s\n' "$*"; }

usage() {
    cat <<'USAGE'
usage: ./build.sh --target nurbs|mesh|axis [options]

targets
  mesh   MeshPreprocessingHeadless    OBJ/point cloud -> mesh stage
  nurbs  EdgeLineExtractionHeadless   surface / breakline stage (needs alglib/)
  axis   AxisExtractionHeadless       axis of symmetry (annotated experiment only)

variants
  default         pcl_191_nurbs.sif, no cmake -D      (what build_mesh.sh did)
  release         pcl_191_nurbs.sif, -DCMAKE_BUILD_TYPE=Release
  working-pcl112  sfs_preprocessing_working.sif       (legacy PCL 1.12 image)

options
  --container PATH  use this image instead of the variant's
  --build-dir DIR   default build/<target>-<variant>; needs a single --target
  --jobs N          parallelism given to make (default: nproc)
  --dry-run         print the container command and exit without running it
USAGE
}

while [ $# -gt 0 ]; do
    case "$1" in
        --target)      [ $# -ge 2 ] || die "--target needs a value"; TARGETS+=("$2"); shift 2 ;;
        --target=*)    TARGETS+=("${1#*=}"); shift ;;
        --variant)     [ $# -ge 2 ] || die "--variant needs a value"; VARIANT="$2"; shift 2 ;;
        --variant=*)   VARIANT="${1#*=}"; shift ;;
        --build-dir)   [ $# -ge 2 ] || die "--build-dir needs a value"; BUILD_DIR="$2"; shift 2 ;;
        --build-dir=*) BUILD_DIR="${1#*=}"; shift ;;
        --container)   [ $# -ge 2 ] || die "--container needs a value"; CONTAINER="$2"; shift 2 ;;
        --container=*) CONTAINER="${1#*=}"; shift ;;
        --jobs)        [ $# -ge 2 ] || die "--jobs needs a value"; JOBS="$2"; shift 2 ;;
        --jobs=*)      JOBS="${1#*=}"; shift ;;
        --dry-run)     DRY_RUN=1; shift ;;
        -h|--help)     usage; exit 0 ;;
        *)             die "unknown argument: $1 (try --help)" ;;
    esac
done

[ "${#TARGETS[@]}" -gt 0 ] || { usage >&2; die "--target is required"; }

# --target takes repeats and commas: '--target mesh,nurbs' == two --target flags.
EXPANDED=()
for t in "${TARGETS[@]}"; do
    IFS=',' read -r -a _parts <<< "$t"
    for p in "${_parts[@]}"; do [ -n "$p" ] && EXPANDED+=("$p"); done
done
TARGETS=("${EXPANDED[@]}")

if [ -n "$BUILD_DIR" ] && [ "${#TARGETS[@]}" -gt 1 ]; then
    die "--build-dir names one directory, so it needs exactly one --target"
fi

# ---- the axis target is refused here, by decision (ticket 277) -------------
# Ticket 277: --target axis has NEVER compiled. axis_extraction_cpp.cpp asks for
# Eigen::Vector6d at lines 21, 159 and 193, a type this Eigen does not have, and
# no tracked CMakeLists carries an AxisExtractionHeadless target: 3bd5c10 added
# it, e34db86 removed it ("axis extraction runs via MATLAB"). The interface keeps
# the target, so the caller meets the decision here instead of a compiler error
# inside the container. Nothing is configured, nothing is built.
# DELETE THIS FUNCTION AND ITS CALL once the port actually compiles.
refuse_unbuilt_axis() {
    case "$1" in
        axis) ;;
        *) return 0 ;;
    esac
    cat >&2 <<'EOF'
build.sh: --target axis is refused: this target has never compiled.

  The source asks for a type the toolchain does not have -- Eigen::Vector6d, at
  axis_extraction_cpp.cpp:21, :159 and :193 -- and no CMake or CI build target
  for AxisExtractionHeadless exists: commit 3bd5c10 added it, e34db86 removed it
  because axis extraction runs via MATLAB.

  The reason is recorded in ticket 277:
    .scratch/pota-repro/issues/277-axis-target-does-not-compile.md

  Nothing was built, and cmake was never run. Exit 4 means "not buildable by
  decision", which a caller can tell apart from a compile failure.
EOF
    exit 4
}

for _t in "${TARGETS[@]}"; do refuse_unbuilt_axis "$_t"; done

# ---- variants: image + cmake arguments -------------------------------------
# A variant is a configuration, not a copy of the tree. The image can still be
# overridden with --container, which is how a candidate image is tried without
# inventing a variant name for it.
variant_container() {
    case "$1" in
        default|release) echo "${REPO_ROOT}/pcl_191_nurbs.sif" ;;
        working-pcl112)  echo "${REPO_ROOT}/sfs_preprocessing_working.sif" ;;
        *)               return 1 ;;
    esac
}

variant_cmake_args() {
    case "$1" in
        default)        echo "" ;;
        release)        echo "-DCMAKE_BUILD_TYPE=Release" ;;
        working-pcl112) echo "" ;;
        *)              return 1 ;;
    esac
}

variant_cmake_args "$VARIANT" >/dev/null || \
    die "unknown variant '$VARIANT' (known: default, release, working-pcl112)"

[ -n "$CONTAINER" ] || CONTAINER="$(variant_container "$VARIANT")"
[ -n "$JOBS" ] || JOBS="$(nproc 2>/dev/null || echo 4)"

# Quote one word for the inner 'bash -c' that runs inside the container.
shellq() { printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"; }

# ---- the property that matters most, measured ------------------------------
# Ignored paths (build/, *.sif, original_nurbs_preprocessing/alglib/) never appear
# here, so "clean" really means "no source file changed".
status_now() { git -C "$REPO_ROOT" status --porcelain 2>/dev/null || true; }
STATUS_BEFORE="$(status_now)"

# ---- per-target facts -----------------------------------------------------
target_src_dir() {
    case "$1" in
        mesh|nurbs) echo "${REPO_ROOT}/original_nurbs_preprocessing" ;;
        axis)       echo "${REPO_ROOT}" ;;
    esac
}

target_make() {
    case "$1" in
        mesh)  echo MeshPreprocessingHeadless ;;
        nurbs) echo EdgeLineExtractionHeadless ;;
        axis)  echo AxisExtractionHeadless ;;
    esac
}

# Vendored, gitignored prerequisites: a fresh worktree never has them, and
# without this check the build dies deep inside a compiler error instead.
target_prereqs() {
    case "$1" in
        nurbs) echo "original_nurbs_preprocessing/alglib/src/dataanalysis.h" ;;
        *)     echo "" ;;
    esac
}

# The axis target is in NO tracked CMakeLists.txt: commit 3bd5c10 added it to the
# root CMakeLists.txt and commit e34db86 removed it again ("axis extraction runs
# via MATLAB"), while axis_extraction_cpp.cpp stayed in the tree. Instead of
# rewriting a tracked file the way the legacy scripts did, its project file is
# generated inside the build directory and configured with -S build -B build.
write_axis_cmakelists() {
    cat > "$1/CMakeLists.txt" <<EOF
# GENERATED by build.sh -- do not edit, do not commit. It lives in the build
# directory precisely so that building the axis experiment cannot dirty the
# source tree. axis_extraction_cpp.cpp needs Eigen only (no PCL, no CGAL).
cmake_minimum_required(VERSION 3.10)
project(AxisExtraction LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
find_path(EIGEN_INCLUDE_DIR Eigen/Dense PATHS /usr/include/eigen3 /usr/local/include/eigen3)
if(NOT EIGEN_INCLUDE_DIR)
  message(FATAL_ERROR "Eigen not found (looked in /usr/include/eigen3, /usr/local/include/eigen3)")
endif()
include_directories(\${EIGEN_INCLUDE_DIR})
# CMake has no single-quote quoting: a 'path' keeps the quotes in the filename and
# cmake reports the source as missing. The path must be in double quotes.
add_executable(AxisExtractionHeadless "$2")
EOF
}

# /data is the project tree on Spartan. When the worktree lives elsewhere (a
# /scratch worktree, a smoke test outside /data) bind it explicitly.
bind_args() {
    if [ -d /data ] && [ -w /data ]; then
        echo "--bind"
        echo "/data:/data"
    fi
    case "$REPO_ROOT" in
        /data/*) ;;
        *) echo "--bind"; echo "${REPO_ROOT}:${REPO_ROOT}" ;;
    esac
}

# ---- run ------------------------------------------------------------------
[ -f "$CONTAINER" ] || die "container not found: $CONTAINER
  variant '$VARIANT' expects that image. It was provisioned by build_working.sh /
  build_final_working.sh, which no longer exist on the cluster. Reprovision it, or
  point at an existing image with --container PATH."
if [ "$DRY_RUN" -eq 0 ] && [ ! -x "$APPTAINER" ]; then
    die "apptainer not found at $APPTAINER (override with APPTAINER=/path/to/apptainer)"
fi

mapfile -t BINDS < <(bind_args)

FAILED=0
for TARGET in "${TARGETS[@]}"; do
    MAKE_TARGET="$(target_make "$TARGET" 2>/dev/null)"
    [ -n "$MAKE_TARGET" ] || die "unknown target '$TARGET' (known: mesh, nurbs, axis)"

    SRC_DIR="$(target_src_dir "$TARGET")"
    DIR="${BUILD_DIR:-${REPO_ROOT}/build/${TARGET}-${VARIANT}}"
    CMAKE_ARGS="$(variant_cmake_args "$VARIANT") -DCMAKE_EXPORT_COMPILE_COMMANDS=ON"

    [ -d "$SRC_DIR" ] || die "source directory missing: $SRC_DIR"
    for rel in $(target_prereqs "$TARGET"); do
        [ -f "${REPO_ROOT}/$rel" ] && continue
        die "vendored prerequisite missing: ${REPO_ROOT}/$rel
  target '$TARGET' needs it: original_nurbs_preprocessing/edgeline_extraction_headless.cpp:93
  includes \"alglib/src/dataanalysis.h\" and the file uses namespace alglib.
  alglib/ is gitignored, so a fresh worktree never has it. Provision it once,
  outside this script:
    cp -a /data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing/alglib ${REPO_ROOT}/original_nurbs_preprocessing/
  It is third-party source, not build output, so git status stays clean either way."
    done

    mkdir -p "$DIR"
    DIR="$(cd -- "$DIR" && pwd -P)"

    # A worktree builds itself: a --build-dir outside it is how two checkouts end
    # up sharing objects, which is the drift this script exists to stop.
    case "$DIR" in
        "$REPO_ROOT"/*) ;;
        *) die "--build-dir must be inside the worktree ($REPO_ROOT), got $DIR" ;;
    esac
    git -C "$REPO_ROOT" check-ignore -q "$DIR" || \
        say "build.sh: warning: $DIR is not gitignored -- add it, or the tree stops staying clean" >&2

    if [ "$TARGET" = axis ]; then
        write_axis_cmakelists "$DIR" "${SRC_DIR}/axis_extraction_cpp.cpp"
        CMAKE_SRC="$DIR"
    else
        CMAKE_SRC="$SRC_DIR"
    fi

    INNER="cmake -S $(shellq "$CMAKE_SRC") -B $(shellq "$DIR") ${CMAKE_ARGS} && make -C $(shellq "$DIR") -j${JOBS} ${MAKE_TARGET}"
    CMD=( "$APPTAINER" exec "${BINDS[@]}" "$CONTAINER" /bin/bash -c "$INNER" )

    say "=============================================================="
    say "target    : ${TARGET}  (make ${MAKE_TARGET})"
    say "variant   : ${VARIANT}"
    say "container : ${CONTAINER}"
    say "source    : ${CMAKE_SRC}"
    say "build dir : ${DIR}"
    say "command   : ${CMD[*]}"
    say "=============================================================="

    if [ "$DRY_RUN" -eq 1 ]; then
        say "(dry run: nothing executed)"
        continue
    fi

    rc=0
    # No '| tail' on the build: piping swallows the exit code, and that is how a
    # legacy run once reported BUILD-EXIT=0 for a target that did not exist.
    "${CMD[@]}" || rc=$?
    if [ "$rc" -ne 0 ]; then
        say "build.sh: target '${TARGET}' FAILED (exit ${rc})" >&2
        FAILED=$rc
        continue
    fi
    if [ ! -x "${DIR}/${MAKE_TARGET}" ]; then
        say "build.sh: make succeeded but ${DIR}/${MAKE_TARGET} is missing or not executable" >&2
        FAILED=1
        continue
    fi

    SHA="$(sha256sum "${DIR}/${MAKE_TARGET}" | cut -d' ' -f1)"
    # Provenance: a binary on disk traces back to the image and flags that made it.
    printf 'target=%s\nvariant=%s\ncontainer=%s\nsource=%s\ncmake_args=%s\nmake=%s -j%s\nbuilt=%s\nsha256=%s\n' \
        "$TARGET" "$VARIANT" "$CONTAINER" "$CMAKE_SRC" "$CMAKE_ARGS" "$MAKE_TARGET" "$JOBS" \
        "$(date -Is)" "$SHA" > "${DIR}/build-info.txt"

    say "built     : ${DIR}/${MAKE_TARGET}"
    say "size      : $(stat -c %s "${DIR}/${MAKE_TARGET}") bytes"
    say "sha256    : $SHA"
done

[ "$DRY_RUN" -eq 1 ] && exit 0

# ---- prove it left the tree alone ----------------------------------------
STATUS_AFTER="$(status_now)"
if [ "$STATUS_BEFORE" != "$STATUS_AFTER" ]; then
    say "build.sh: ERROR: the build changed git status. This must never happen." >&2
    printf '%s\n' "$STATUS_BEFORE" > /tmp/status-before.txt
    printf '%s\n' "$STATUS_AFTER"  > /tmp/status-after.txt
    diff /tmp/status-before.txt /tmp/status-after.txt >&2 || true
    exit 3
fi
if [ -z "$STATUS_AFTER" ]; then
    say "git status --porcelain: empty before and after the build"
else
    say "git status --porcelain: unchanged before and after ($(printf '%s\n' "$STATUS_AFTER" | wc -l) pre-existing entries)"
fi

[ "$FAILED" -eq 0 ] || exit "$FAILED"
say "OK"
