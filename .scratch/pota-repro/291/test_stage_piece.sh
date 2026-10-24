#!/usr/bin/env bash
# Local functional test of scripts/stage_piece.sh against a SYNTHETIC corpus: no Spartan, no geometry.
# Proves the guard rails and the bookkeeping. Whether this filesystem can make a symlink is probed
# first: where it cannot, the script must refuse rather than stage a copy, and the symlink itself is
# proved on the cluster by the ticket-291 gate job instead.
set -uo pipefail

HERE=$(cd "$(dirname "$0")" && pwd -P)
REPO=$(cd "$HERE/../../.." && pwd -P)
SP=$REPO/scripts/stage_piece.sh
pass=0; fail=0
ok()   { pass=$((pass+1)); echo "PASS  $*"; }
bad()  { fail=$((fail+1)); echo "FAIL  $*"; }
check() { # check <label> <expected exit> <cmd...>
  local label=$1 want=$2; shift 2
  "$@" >"$LOG" 2>&1; local got=$?
  if [ "$got" = "$want" ]; then ok "$label (exit $got)"; else bad "$label (exit $got, wanted $want)"; sed "s/^/      /" "$LOG"; fi
}
expect_text() { # expect_text <label> <pattern>
  if grep -q "$2" "$LOG"; then ok "$1"; else bad "$1 (log: $(tail -2 "$LOG" | tr "\n" " "))"; fi
}

TMP=$(mktemp -d); LOG=$TMP/log.txt
COR=$TMP/corpus
mkdir -p "$COR/Mesh" "$COR/Point/Pot_X" "$COR/Axes"
printf "v 1\nv 2\nv 3\nf 1 2 3\n" > "$COR/Mesh/Pot_X_Piece_01_Mesh_DS.obj"
printf "v 1\nv 2\nv 3\nf 1 2 3\n" > "$COR/Mesh/Pot_X_Piece_02_Mesh_DS.obj"
printf "# .PCD v0.7 - Point Cloud Data file format\nVERSION .7\nFIELDS x y z\nSIZE 4 4 4\nTYPE F F F\nCOUNT 1 1 1\nWIDTH 1234\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\nPOINTS 1234\nDATA ascii\n0 0 0\n" > "$COR/Point/Pot_X/Pot_X_Piece_01_Point.pcd"
printf "0 0 0\n1 0 0\n" > "$COR/Axes/Pot_X_Piece_01_Axis.xyz"
CM=$(md5sum "$COR/Point/Pot_X/Pot_X_Piece_01_Point.pcd" | awk '{print $1}')
write_manifests() {
  printf "pot\tpiece\tpoints\tbytes\tmd5\theader_ok\nPot_X\tPot_X_Piece_01\t1234\t1\t%s\tok\n" "$1" > "$COR/Point/MANIFEST_released.tsv"
  printf "piece\tsource_mesh\tmesh_md5\tpoints\tpcd_md5\tbytes\n" > "$COR/Point/MANIFEST_derived.tsv"
}
write_manifests "$CM"

# capability probe: can this filesystem hold a symlink at all?
CAN_LINK=0
echo probe > "$TMP/probe.txt"
ln -s "$TMP/probe.txt" "$TMP/probe.lnk" 2>/dev/null
[ -L "$TMP/probe.lnk" ] && CAN_LINK=1
echo "symlink_capable=$CAN_LINK"
echo

if [ "$CAN_LINK" = 1 ]; then
  echo "=== A: happy path, _DS mesh fallback, released manifest"
  check "A1 stage succeeds" 0 env SFS_CORPUS="$COR" bash "$SP" "$TMP/stageA" Pot_X Pot_X_Piece_01
  SA=$TMP/stageA
  [ -L "$SA/Dataset/Mesh/Pot_X/Pot_X_Piece_01_Mesh.obj" ] && ok "A2 mesh is a symlink" || bad "A2 mesh is a symlink"
  [ -L "$SA/Dataset/Point/Pot_X/Pot_X_Piece_01_Point.pcd" ] && ok "A3 cloud is a symlink" || bad "A3 cloud is a symlink"
  [ -f "$SA/Dataset/Axes/Pot_X_Piece_01_Axis.xyz" ] && [ ! -L "$SA/Dataset/Axes/Pot_X_Piece_01_Axis.xyz" ] && ok "A4 axis is a copied real file" || bad "A4 axis copied"
  [ "$(readlink -f "$SA/Dataset/Mesh/Pot_X/Pot_X_Piece_01_Mesh.obj")" = "$(readlink -f "$COR/Mesh/Pot_X_Piece_01_Mesh_DS.obj")" ] && ok "A5 mesh resolves to the _DS corpus file" || bad "A5 mesh resolves to the _DS corpus file"
  [ "$(awk -F"\t" "NR>1" "$SA/inputs.md5" | wc -l)" = 3 ] && ok "A6 inputs.md5 has 3 data rows (mesh, cloud, axis)" || bad "A6 inputs.md5 rows: $(awk -F"\t" "NR>1" "$SA/inputs.md5" | wc -l)"
  awk -F"\t" "NR>1 && \$3==1234" "$SA/inputs.md5" | grep -q . && ok "A7 cloud row carries POINTS 1234" || bad "A7 cloud row carries POINTS 1234"
  for d in Dataset/Breaklines/Pot_X Dataset/Surfaces/Pot_X Dataset/Mesh/Pot_X Temp/Data/Pot_X Temp/Temp_edge/Pot_X; do [ -d "$SA/$d" ] && ok "A8 dir $d" || bad "A8 dir $d"; done
  expect_text "A9 summary counts 2 symlinks and 18 copied bytes" "symlinks=2 copied_files=1 copied_bytes=18"
  echo
  echo "=== B: rerun into the same stage"
  check "B1 rerun succeeds" 0 env SFS_CORPUS="$COR" bash "$SP" "$TMP/stageA" Pot_X Pot_X_Piece_01
  [ "$(find "$SA" -type l | wc -l)" = 2 ] && ok "B2 still exactly 2 symlinks" || bad "B2 symlink count $(find "$SA" -type l | wc -l)"
  [ "$(awk -F"\t" "NR>1" "$SA/inputs.md5" | wc -l)" = 6 ] && ok "B3 inputs.md5 appended (6 rows)" || bad "B3 inputs.md5 rows $(awk -F"\t" "NR>1" "$SA/inputs.md5" | wc -l)"
else
  echo "=== A: SKIPPED - this filesystem cannot create a symlink; the cluster gate job proves it"
  echo "=== A0: on such a filesystem the script must refuse rather than copy"
  check "A0 stage refuses instead of copying" 1 env SFS_CORPUS="$COR" bash "$SP" "$TMP/stageA0" Pot_X Pot_X_Piece_01
  expect_text "A0b the refusal names the missing symlink support" "cannot create symlinks"
  [ "$(find "$TMP/stageA0" -type f -size +10c | wc -l)" = 0 ] && ok "A0c no geometry-like file left in the stage" || bad "A0c files left: $(find "$TMP/stageA0" -type f -size +10c)"
fi
echo

echo "=== C: guard rails (all must fail before any staging)"
check "C1 missing cloud refuses (never derives)" 1 env SFS_CORPUS="$COR" bash "$SP" "$TMP/stageC" Pot_X Pot_X_Piece_02
expect_text "C2 the refusal names the reason" "Refusing to derive one"
[ "$(find "$TMP/stageC" -type d 2>/dev/null | wc -l)" = 0 ] && ok "C2b nothing was created for the missing-cloud piece" || bad "C2b stage tree was created: $(find "$TMP/stageC" | head -3)"
mkdir -p "$TMP/stageD/Dataset/Mesh/Pot_X"
printf "not a symlink\n" > "$TMP/stageD/Dataset/Mesh/Pot_X/Pot_X_Piece_01_Mesh.obj"
check "C3 existing regular file is not replaced" 1 env SFS_CORPUS="$COR" bash "$SP" "$TMP/stageD" Pot_X Pot_X_Piece_01
expect_text "C4 the refusal names the file rule" "refusing to replace an existing regular file"
[ "$(cat "$TMP/stageD/Dataset/Mesh/Pot_X/Pot_X_Piece_01_Mesh.obj")" = "not a symlink" ] && ok "C4b the existing file was left untouched" || bad "C4b the existing file changed"
check "C5 stage inside the corpus refused" 1 env SFS_CORPUS="$COR" bash "$SP" "$COR/stageE" Pot_X Pot_X_Piece_01
check "C6 piece must belong to the pot" 1 env SFS_CORPUS="$COR" bash "$SP" "$TMP/stageF" Pot_X Pot_Y_Piece_01
write_manifests deadbeef
check "C7 manifest cloud md5 mismatch refuses" 1 env SFS_CORPUS="$COR" bash "$SP" "$TMP/stageG" Pot_X Pot_X_Piece_01
expect_text "C8 the refusal names the manifest" "corpus manifest disagrees"
write_manifests "$CM"

echo
echo "=== result: $pass passed, $fail failed"
rm -rf "$TMP"
[ "$fail" = 0 ]
