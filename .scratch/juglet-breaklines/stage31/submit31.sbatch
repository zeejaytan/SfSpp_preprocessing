#!/usr/bin/env bash
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --job-name=p31probe
#SBATCH --time=00:40:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --output=logs/slurm-%j.out
#
# Ticket 31 -- re-score the Pot A control on a compute node, from a numpy-only
# port of the p07 gate probe, and prove the port faithful by reproducing the
# laptop's own fifteen per-pair lines.
#
# Nothing here rebuilds the pipeline and nothing here scores on the login node.
# The job unpacks the p07 bundle (unchanged md5), renames its eight breakline
# files exactly as the laptop README did, and measures the same bytes three ways:
#
#   A  gate_probe_b0_p07.py       the ORIGINAL script, unmodified, run from a cwd
#                                 that makes its hard-coded C:/PR/... path resolve,
#                                 under the interpreter that HAS scipy -- so the
#                                 original cKDTree search runs on the node.
#   B  gate_probe_p31.py          the port, bruteforce search, under the shipped
#                                 python3 (3.11, numpy only, no scipy).
#   C  gate_probe_p31.py --nn ckdtree
#                                 the port, original search, under the scipy
#                                 interpreter -- isolates the roots/argparse
#                                 changes from the search swap.
#
# A against the laptop is the faithful-reproduction claim. B against A is the
# port's. C against A shows the search is not what moved, if anything did.
set -uo pipefail

STAGE=.scratch/juglet-breaklines/stage31
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
GTDIR="$CORP/Ground Truth"
BUNDLE=/data/gpfs/projects/punim2657/SfSpp/runs/20261027-0055_d8af9d2_p07-juglet-stage1/out/stage1_out.tgz
BUNDLE_MD5=0d823524f974d2ac8fe6b0f3428ed007
BUNDLE_BYTES=11654126
PY_NOSCIPY=/data/gpfs/projects/punim2657/.conda/envs/graphify/bin/python3
PY_SCIPY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3

say() { echo "[RUN] $*"; }
md5_of() { md5sum "$1" | awk '{print $1}'; }
crlf_check() {  # <file>: report, and fail, if the file holds a CR
    if cmp -s "$1" <(tr -d '\r' < "$1"); then
        echo "[RUN] crlf $1: LF only"
    else
        echo "[RUN] crlf $1: CONTAINS CR -- do not run this"
        return 1
    fi
}

source /data/gpfs/projects/punim2657/agent/pr-workspace/scripts/run_from_commit.sh \
    "$CANONICAL" "$SOURCE_COMMIT" "$RUN_DIR"
RUN=$RUN_DIR
OUT=$RUN/out
W=$RUN/work
mkdir -p "$OUT" "$W"
say "node=$(hostname) job=$(printenv SLURM_JOB_ID) start=$(date -Is) commit=$SOURCE_COMMIT"
say "src=$SRC (the commit unpacked by run_from_commit.sh)"

# ---- 1. the scripts about to run: line endings first (the grid killer) ----
# Hard gate, for the files authored here: these are the ones that run as bash or
# whose shebang-free import path I control.
for f in "$SRC/$STAGE/gate_probe_p31.py" "$SRC/$STAGE/compare_p31.py" \
         "$RUN_DIR/submit.sbatch"; do
    crlf_check "$f" || say "CRLF above is fatal for $f"
done
# The laptop's own files are kept byte for byte. They ARE CRLF and the CR must
# still be there -- that is the byte-identity claim. python runs a CRLF source
# file unchanged, so the original probe is run exactly as it was fetched.
{
    echo "# the laptop files: md5 and CR count, byte-identity with the machine that scored this bundle"
    for f in orig/gate_probe_b0_p07.py orig/gate_probe_b0.py orig/README.txt \
             orig/checks_p07.py orig/checks_p07.out laptop/gate_probe_p07.out; do
        printf '%s  CR=%-4s %s\n' "$(md5_of "$SRC/$STAGE/$f")" \
            "$(tr -dc '\015' < "$SRC/$STAGE/$f" | wc -c)" "$f"
    done
    echo "# authored here: must be LF (the crlf_check above is the hard gate)"
    for f in gate_probe_p31.py compare_p31.py; do
        printf '%s  CR=%-4s %s\n' "$(md5_of "$SRC/$STAGE/$f")" \
            "$(tr -dc '\015' < "$SRC/$STAGE/$f" | wc -c)" "$f"
    done
} > "$OUT/stage31_md5.tsv"
say "stage31 file md5s and CR counts in out/stage31_md5.tsv"

# ---- 2. interpreters, and whether scipy is there ----
{
    "$PY_NOSCIPY" - <<'PYEOF'
import sys, numpy
print("shipped_python", sys.executable)
print("python", sys.version.split()[0])
print("numpy", numpy.__version__)
try:
    import scipy
    print("scipy", scipy.__version__)
except Exception as exc:
    print("scipy", "ABSENT", type(exc).__name__)
PYEOF
    "$PY_SCIPY" - <<'PYEOF'
import sys, numpy
print("scipy_python", sys.executable)
print("python", sys.version.split()[0])
print("numpy", numpy.__version__)
try:
    import scipy
    print("scipy", scipy.__version__)
except Exception as exc:
    print("scipy", "ABSENT", type(exc).__name__)
PYEOF
} > "$OUT/env.txt" 2>&1
say "interpreters: $(tr '\n' '; ' < "$OUT/env.txt")"

# ---- 3. read-only state before: frozen corpus, canonical checkout, pristine ----
corpus_manifest() {  # <out.tsv>
    : > "$1"
    local N P f
    for f in "$GTDIR"/Pot_A_Piece_*_T.txt "$GTDIR"/Pot_A_simple_graph.txt; do
        [ -f "$f" ] && printf '%s\t%s\n' "$(md5_of "$f")" "$f" >> "$1"
    done
    for N in 1 2 3 4 5 6 7 8; do
        P=$(printf "Pot_A_Piece_%02d" "$N")
        for f in "$CORP/Axes/$P"_Axis.xyz "$CORP/Mesh/$P"_Mesh.obj \
                 "$CORP/Point/Pot_A/$P"_Point.pcd \
                 "$CORP/Surfaces/$P"_Surface_0.xyz "$CORP/Surfaces/$P"_Surface_1.xyz \
                 "$CORP/Breaklines/Pot_A/$P"_Breakline_0.pcd \
                 "$CORP/Breaklines/Pot_A/$P"_Breakline_1.pcd; do
            [ -f "$f" ] && printf '%s\t%s\n' "$(md5_of "$f")" "$f" >> "$1"
        done
    done
}
canonical_state() {  # <out.txt>
    {
        echo "head=$(git -C "$CANON" rev-parse HEAD)"
        echo "porcelain_lines=$(git -C "$CANON" status --porcelain | wc -l)"
        echo "skip_worktree_files=$(git -C "$CANON" ls-files -v | grep -c '^S')"
        for f in edgeline_extraction_headless.cpp mesh_processing_headless.cpp data_path.h; do
            printf '%s\t%s\n' "$f" "$(md5_of "$CANON/$f")"
        done
    } > "$1"
}
corpus_manifest "$OUT/corpus_md5_before.tsv"
canonical_state "$OUT/canonical_before.txt"
say "corpus files hashed before: $(wc -l < "$OUT/corpus_md5_before.tsv")"
if [ -e /opt/sfs-pristine ]; then
    echo "PRESENT" > "$OUT/pristine.txt"
else
    echo "ABSENT" > "$OUT/pristine.txt"
fi
say "/opt/sfs-pristine: $(cat "$OUT/pristine.txt")"

# ---- 4. the bundle: same bytes the laptop scored ----
if [ -f "$BUNDLE" ]; then
    bm=$(md5_of "$BUNDLE")
    bb=$(stat -c %s "$BUNDLE")
    if [ "$bm" = "$BUNDLE_MD5" ] && [ "$bb" = "$BUNDLE_BYTES" ]; then
        match=yes
    else
        match=no
    fi
    printf 'bundle=%s\nmd5=%s\nexpected_md5=%s\nbytes=%s\nexpected_bytes=%s\nmd5_and_bytes_match=%s\n' \
        "$BUNDLE" "$bm" "$BUNDLE_MD5" "$bb" "$BUNDLE_BYTES" "$match" > "$OUT/bundle_check.txt"
    say "bundle md5 $bm ($bb B) match=$match"
else
    say "FATAL bundle not found at $BUNDLE"
    printf 'bundle=%s\nstatus=MISSING\n' "$BUNDLE" > "$OUT/bundle_check.txt"
    exit 2
fi

# ---- 5. unpack, and rename the eight Bl0 files the way the laptop README did ----
mkdir -p "$W/stage1"
tar xzf "$BUNDLE" -C "$W/stage1"
say "tar exit=$? files=$(find "$W/stage1" -type f | wc -l)"
find "$W/stage1" -type f -printf '%s\t%p\n' | sort -k2 > "$OUT/bundle_listing.tsv"
cd "$W/stage1" && md5sum $(find . -name 'Pot_A_Piece_*.pcd' -printf '%p ') > "$OUT/bundle_bl0_source_md5.tsv" 2>/dev/null
cd "$RUN"

# The original probe hard-codes ART = "C:/PR/structure-from-sherds-pp/artifacts".
# On Linux that is a RELATIVE path, so a directory named C: makes the unmodified
# script resolve to files this job just unpacked. Nothing is patched.
FAKE="$W/cwdcompat"
BLD="$FAKE/C:/PR/structure-from-sherds-pp/artifacts/p07_stage1/pota_bl"
GTD="$FAKE/C:/PR/structure-from-sherds-pp/artifacts/pota_gt"
mkdir -p "$BLD" "$GTD"
: > "$OUT/bl_md5.tsv"
for N in 1 2 3 4 5 6 7 8; do
    P=$(printf "%02d" "$N")
    cp -f "$W/stage1/geom/Pot_A_Piece_$P.Bl0.pcd" \
          "$BLD/Pot_A_Piece_${P}_Breakline_0.pcd" || say "copy FAILED for piece $P"
    printf '%s\t%s\t%s\t%s\n' "$(md5_of "$BLD/Pot_A_Piece_${P}_Breakline_0.pcd")" \
        "$(stat -c %s "$BLD/Pot_A_Piece_${P}_Breakline_0.pcd")" \
        "$(wc -l < "$BLD/Pot_A_Piece_${P}_Breakline_0.pcd")" \
        "Pot_A_Piece_${P}_Breakline_0.pcd" >> "$OUT/bl_md5.tsv"
done
cp -f "$GTDIR"/Pot_A_Piece_*_T.txt "$GTD"/
cp -f "$GTDIR/Pot_A_simple_graph.txt" "$GTD"/
: > "$OUT/gt_copy_check.tsv"
for f in "$GTD"/*; do
    b=$(basename "$f")
    printf '%s\t%s\t%s\t%s\n' "$b" "$(md5_of "$f")" "$(md5_of "$GTDIR/$b")" \
        "$([ "$(md5_of "$f")" = "$(md5_of "$GTDIR/$b")" ] && echo same || echo DIFFER)" \
        >> "$OUT/gt_copy_check.tsv"
done
say "bl_md5.tsv: $(wc -l < "$OUT/bl_md5.tsv") renamed files; gt copies: $(sort -u -k4 "$OUT/gt_copy_check.tsv" | cut -f4 | tr '\n' ' ')"

# ---- 6. A: the original script, unmodified, with scipy ----
cd "$FAKE"
say "cwd for the original probe: $(pwd)"
"$PY_SCIPY" "$SRC/$STAGE/orig/gate_probe_b0_p07.py" p07 > "$OUT/gate_probe_orig_p07.out" 2>&1
say "A original gate_probe_b0_p07.py (scipy cKDTree) exit=$?"
tail -1 "$OUT/gate_probe_orig_p07.out" | sed 's/^/[RUN] A last line: /'

# ---- 7. B: the port, bruteforce, the shipped python3 without scipy ----
"$PY_NOSCIPY" "$SRC/$STAGE/gate_probe_p31.py" p31 --bl "$BLD" --gt "$GTDIR" \
    > "$OUT/gate_probe_p31.out" 2>&1
say "B port bruteforce (no scipy) exit=$?"
tail -1 "$OUT/gate_probe_p31.out" | sed 's/^/[RUN] B last line: /'

# ---- 8. C: the port, the original search, with scipy ----
"$PY_SCIPY" "$SRC/$STAGE/gate_probe_p31.py" p31 --bl "$BLD" --gt "$GTDIR" --nn ckdtree \
    > "$OUT/gate_probe_p31_ckdtree.out" 2>&1
say "C port ckdtree (scipy) exit=$?"
tail -1 "$OUT/gate_probe_p31_ckdtree.out" | sed 's/^/[RUN] C last line: /'

# ---- 9. the port's self-test, both ways ----
"$PY_NOSCIPY" "$SRC/$STAGE/gate_probe_p31.py" --selftest > "$OUT/selftest_p31_noscipy.out" 2>&1
say "selftest (no scipy) exit=$?"
"$PY_SCIPY" "$SRC/$STAGE/gate_probe_p31.py" --selftest > "$OUT/selftest_p31_scipy.out" 2>&1
say "selftest (scipy) exit=$?"

# ---- 10. the comparison, with both numbers on any difference ----
tr -d '\r' < "$SRC/$STAGE/laptop/gate_probe_p07.out" > "$OUT/laptop_lf.txt"
: > "$OUT/raw_line_diff.txt"
for f in gate_probe_orig_p07.out gate_probe_p31.out gate_probe_p31_ckdtree.out; do
    echo "=== diff $OUT/laptop_lf.txt $OUT/$f ===" >> "$OUT/raw_line_diff.txt"
    diff "$OUT/laptop_lf.txt" "$OUT/$f" >> "$OUT/raw_line_diff.txt" 2>&1
    echo "[RUN] line diff laptop vs $f exit=$?"
done
"$PY_NOSCIPY" "$SRC/$STAGE/compare_p31.py" \
    --ref "$SRC/$STAGE/laptop/gate_probe_p07.out" \
    --cand "A-original-script=$OUT/gate_probe_orig_p07.out" \
    --cand "B-port-bruteforce=$OUT/gate_probe_p31.out" \
    --cand "C-port-ckdtree=$OUT/gate_probe_p31_ckdtree.out" \
    --out "$OUT/COMPARE.md" > "$OUT/compare.stdout" 2>&1
say "compare exit=$?"
sed 's/^/[RUN] compare: /' "$OUT/compare.stdout"

# ---- 11. geometry goes, the record stays: counted before the delete ----
{
    echo "# Everything this job unpacked or copied, written BEFORE the delete."
    echo "# runid=$(basename "$RUN") job=$(printenv SLURM_JOB_ID) host=$(hostname) at=$(date -Is)"
    echo "# columns: bytes <TAB> md5 <TAB> path"
    find "$W" -type f -exec md5sum {} + | sort -k2 | while read -r h p; do
        printf '%s\t%s\t%s\n' "$(stat -c %s "$p")" "$h" "$p"
    done
    echo "# files=$(find "$W" -type f | wc -l) bytes=$(du -sb "$W" | awk '{print $1}')"
} > "$OUT/deleted_geometry_manifest.txt"
say "manifest written: files=$(find "$W" -type f | wc -l) bytes=$(du -sb "$W" | awk '{print $1}')"
rm -rf "$W"
if [ -e "$W" ]; then say "delete FAILED: $W still exists"; else say "geometry deleted: $W gone, out/ kept"; fi
{
    echo "deleted=$W"
    echo "at=$(date -Is)"
    echo "manifest=$OUT/deleted_geometry_manifest.txt"
    echo "files_in_manifest=$(grep -vc '^#' "$OUT/deleted_geometry_manifest.txt")"
} > "$OUT/deleted_geometry.txt"

# ---- 12. read-only state after, and the corpus verdict ----
corpus_manifest "$OUT/corpus_md5_after.tsv"
canonical_state "$OUT/canonical_after.txt"
if diff -q "$OUT/corpus_md5_before.tsv" "$OUT/corpus_md5_after.tsv" > /dev/null; then
    echo "[RUN] corpus md5 UNCHANGED ($(wc -l < "$OUT/corpus_md5_before.tsv") files)" > "$OUT/corpus_verdict.txt"
else
    echo "[RUN] corpus md5 CHANGED" > "$OUT/corpus_verdict.txt"
    diff "$OUT/corpus_md5_before.tsv" "$OUT/corpus_md5_after.tsv" >> "$OUT/corpus_verdict.txt"
fi
if diff -q "$OUT/canonical_before.txt" "$OUT/canonical_after.txt" > /dev/null; then
    echo "[RUN] canonical checkout UNCHANGED" >> "$OUT/corpus_verdict.txt"
else
    echo "[RUN] canonical checkout CHANGED" >> "$OUT/corpus_verdict.txt"
    diff "$OUT/canonical_before.txt" "$OUT/canonical_after.txt" >> "$OUT/corpus_verdict.txt"
fi
say "corpus verdict: $(tr '\n' '; ' < "$OUT/corpus_verdict.txt")"
say "out/ holds: $(ls -1 "$OUT" | tr '\n' ' ')"
say "done at $(date -Is)"
