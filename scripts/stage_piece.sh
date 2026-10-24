#!/usr/bin/env bash
# stage_piece.sh -- stage one run inputs by symlink into the frozen corpus (ticket 291).
#
#   scripts/stage_piece.sh <stage_dir> <Pot_X> <Piece_01> [<Piece_02> ...]
#
# The pipeline reads a piece from Dataset/{Point,Mesh,Axes}/. A run used to copy every input into
# its stage tree (a 1.3-4.4 MB mesh plus a 20-90 MB cloud per piece); this script links the geometry
# to the frozen corpus instead, so a staged piece carries no geometry of its own. Only the 7 KB axis
# file is copied, and only the output directories are real.
#
# The mesh symlink also absorbs the _DS naming trap: the pipeline derives <Piece>_Mesh.obj from the
# point file stem, and a symlink can carry either corpus variant under that name.
#
# Every input is resolved and checked against the corpus manifests BEFORE anything is staged, so a
# bad corpus leaves no half-built tree behind.
#
# Environment: SFS_CORPUS overrides the corpus root.
set -euo pipefail

CORPUS=${SFS_CORPUS:-/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp}

die() { echo "[STAGE-291] ERROR: $*" >&2; exit 1; }
say() { echo "[STAGE-291] $*"; }

[ $# -ge 3 ] || die "usage: $0 <stage_dir> <Pot_X> <Piece_01> [<Piece_02> ...]"
STAGE_IN=$1; shift
POT=$1; shift
PIECES=("$@")

[ -d "$CORPUS" ] || die "corpus not found: $CORPUS"
case "$POT" in
  Pot_*) : ;;
  *) die "the pot name must look like Pot_X, got "$POT"" ;;
esac
for P in "${PIECES[@]}"; do
  case "$P" in "$POT"_Piece_*) : ;; *) die "piece "$P" does not belong to "$POT"" ;; esac
done

STAGE=$(realpath -m "$STAGE_IN")
CORPUS_REAL=$(cd "$CORPUS" && pwd -P)
case "$STAGE/" in
  "$CORPUS_REAL"/*) die "the stage directory is inside the corpus: $STAGE" ;;
esac


MAN_RELEASED=$CORPUS/Point/MANIFEST_released.tsv
MAN_DERIVED=$CORPUS/Point/MANIFEST_derived.tsv

pcd_points() { # pcd_points <file> -> POINTS from the PCD header
  awk '/^POINTS[[:space:]]/{print $2; exit}' "$1"
}

manifest_md5() { # manifest_md5 <piece> -> the corpus cloud md5, empty when listed in neither manifest
  local p=$1 m=""
  if [ -f "$MAN_RELEASED" ]; then m=$(awk -F'\t' -v p="$p" '$2==p {print $5}' "$MAN_RELEASED"); fi
  if [ -z "$m" ] && [ -f "$MAN_DERIVED" ]; then m=$(awk -F'\t' -v p="$p" '$1==p {print $5}' "$MAN_DERIVED"); fi
  printf '%s' "$m"
}

# ---- phase 1: resolve every input and check it. Nothing is written yet. ----
MESHES=(); CLOUDS=(); AXES=(); POINTCOUNTS=(); MESH_MD5S=(); CLOUD_MD5S=()
i=0
for P in "${PIECES[@]}"; do
  for staged in "$STAGE/Dataset/Mesh/$POT/${P}_Mesh.obj" "$STAGE/Dataset/Point/$POT/${P}_Point.pcd"; do
    if [ -e "$staged" ] && [ ! -L "$staged" ]; then
      die "refusing to replace an existing regular file with a symlink: $staged"
    fi
  done

  MESH=""
  for cand in "$CORPUS/Mesh/$POT/${P}_Mesh.obj" "$CORPUS/Mesh/${P}_Mesh.obj" "$CORPUS/Mesh/$POT/${P}_Mesh_DS.obj" "$CORPUS/Mesh/${P}_Mesh_DS.obj"; do
    if [ -f "$cand" ]; then MESH=$cand; break; fi
  done
  [ -n "$MESH" ] || die "no mesh for $P under $CORPUS/Mesh (looked for plain and _DS, flat and per-pot)"

  CLOUD="$CORPUS/Point/$POT/${P}_Point.pcd"
  if [ ! -f "$CLOUD" ]; then
    die "no cloud for $P at $CLOUD. Refusing to derive one: the mesh sampler takes no seed, so a fresh draw is not reproducible and the run would not repeat. Stage a corpus that holds this piece."
  fi

  AXIS="$CORPUS/Axes/${P}_Axis.xyz"
  [ -f "$AXIS" ] || die "no axis for $P at $AXIS"

  pts=$(pcd_points "$CLOUD")
  [ -n "$pts" ] || die "no POINTS line in the header of $CLOUD"
  mesh_md5=$(md5sum "$MESH" | awk '{print $1}')
  cloud_md5=$(md5sum "$CLOUD" | awk '{print $1}')

  if [ -f "$MAN_DERIVED" ]; then
    dm=$(awk -F'\t' -v p="$P" '$1==p {print $3}' "$MAN_DERIVED")
    if [ -n "$dm" ] && [ "$dm" != "$mesh_md5" ]; then
      die "the derived manifest disagrees for $P: mesh md5 $mesh_md5, manifest $dm"
    fi
  fi
  man=$(manifest_md5 "$P")
  if [ -n "$man" ] && [ "$man" != "$cloud_md5" ]; then
    die "corpus manifest disagrees for $P: cloud md5 $cloud_md5, manifest $man"
  fi

  MESHES[$i]=$MESH; CLOUDS[$i]=$CLOUD; AXES[$i]=$AXIS
  POINTCOUNTS[$i]=$pts; MESH_MD5S[$i]=$mesh_md5; CLOUD_MD5S[$i]=$cloud_md5
  UNLISTED[$i]=""
  [ -n "$man" ] || UNLISTED[$i]="unlisted"
  i=$((i + 1))
done

# ---- phase 2: build the stage. A filesystem without symlink support is refused first, because it
# copies the target instead of linking it -- exactly what this script exists to avoid. ----
PROBE=$(mktemp -d)
echo probe > "$PROBE/target"
ln -s "$PROBE/target" "$PROBE/link" 2>/dev/null || true
if [ ! -L "$PROBE/link" ]; then
  rm -rf "$PROBE"
  die "this filesystem cannot create symlinks ($STAGE), so a stage here would hold copied geometry. Stage on a filesystem with symlink support."
fi
rm -rf "$PROBE"

mkdir -p "$STAGE"
for d in "Dataset/Mesh/$POT" "Dataset/Point/$POT" "Dataset/Axes" "Dataset/Breaklines/$POT" "Dataset/Surfaces/$POT" "Temp/Data/$POT" "Temp/Temp_edge/$POT"; do
  mkdir -p "$STAGE/$d"
done

INPUTS=$STAGE/inputs.md5
[ -e "$INPUTS" ] || printf 'md5\trealpath\tpoints\tstaged\n' > "$INPUTS"

links=0; copied_files=0; copied_bytes=0

link_into() { # link_into <corpus file> <staged path>
  local target=$1 staged=$2
  if [ -e "$staged" ] && [ ! -L "$staged" ]; then
    die "refusing to replace an existing regular file with a symlink: $staged"
  fi
  if [ -L "$staged" ]; then
    local old
    old=$(readlink -f "$staged" || true)
    [ "$old" = "$(readlink -f "$target")" ] || say "relinked $staged (was $old)"
  fi
  ln -sfn "$target" "$staged"
  [ -L "$staged" ] || die "ln -s did not produce a symlink at $staged: this filesystem copies the target instead, so the stage would hold real geometry. Stage on a filesystem with symlink support."
  links=$((links + 1))
}

record() { # record <staged path> <points or ->
  printf '%s\t%s\t%s\t%s\n' "$(md5sum "$1" | awk '{print $1}')" "$(readlink -f "$1")" "$2" "$1" >> "$INPUTS"
}

for i in "${!PIECES[@]}"; do
  P=${PIECES[$i]}
  MESH_STAGED="$STAGE/Dataset/Mesh/$POT/${P}_Mesh.obj"
  CLOUD_STAGED="$STAGE/Dataset/Point/$POT/${P}_Point.pcd"
  AXIS_STAGED="$STAGE/Dataset/Axes/${P}_Axis.xyz"

  link_into "${MESHES[$i]}" "$MESH_STAGED"
  link_into "${CLOUDS[$i]}" "$CLOUD_STAGED"
  cp -f "${AXES[$i]}" "$AXIS_STAGED"
  copied_files=$((copied_files + 1))
  copied_bytes=$((copied_bytes + $(stat -c %s "${AXES[$i]}")))

  record "$MESH_STAGED" "-"
  record "$CLOUD_STAGED" "${POINTCOUNTS[$i]}"
  record "$AXIS_STAGED" "-"

  [ -z "${UNLISTED[$i]}" ] || say "WARNING $P is in neither corpus manifest; recorded without a manifest check"
  say "$P: mesh $(basename "$(readlink -f "${MESHES[$i]}")") md5=${MESH_MD5S[$i]} | cloud md5=${CLOUD_MD5S[$i]} points=${POINTCOUNTS[$i]} | both from $CORPUS_REAL"
done

say "pieces=${#PIECES[@]} pot=$POT symlinks=$links copied_files=$copied_files copied_bytes=$copied_bytes stage=$STAGE"
