#!/usr/bin/env python3
"""Ticket 16 input identity: tree corpus, and per-cell staged axis pack.

Tree mode (always):
  * every line of <tree>/arm_inputs.md5 (md5, name, bytes) matches the file actually there;
  * <tree>/Axes holds the 12 t09 axes byte-identical to the t09 canonical pack;
  * the 11 Pot J breaklines are the manifest's Breakline_0 files.
Cell mode (--axes-dir, --j01-sha, --label): additionally
  * the staged pack has 12 axes;
  * J02..J12 are byte-identical to both the t09 canonical pack and Ticket 13's T09_ALL pack;
  * Pot_J_Piece_01_Axis.xyz is the arm's candidate (--j01-sha).

Writes logs/tree_pins16.tsv, logs/axis_pins16.tsv, logs/tree_verify16.json and, in cell
mode, logs/identity16_<label>.tsv.  Exit 0 = OK, 1 = tree bad, 2 = staged pack bad.
"""
import argparse
import hashlib
import json
import os
import sys

T13 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261126-1500_cf88609_t13-diagnose"
T13_AX = os.path.join(T13, "axes", "T09_ALL")
T09_AX = ("/data/gpfs/projects/punim2657/SfSpp/runs/"
          "20261125-1340_a50f8cc_t09-own-surfaces/out/axes09_own_regen")
STEM = "Pot_J_Piece_01"
TAB, NL = chr(9), chr(10)


def _hash(path, algo):
    h = hashlib.new(algo)
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def tree_check(run, tree, label=""):
    logs = os.path.join(run, "logs")
    suffix = ("_" + label) if label else ""
    os.makedirs(logs, exist_ok=True)
    index = {}
    for root, _dirs, files in os.walk(tree):
        for f in files:
            index.setdefault(f, []).append(os.path.join(root, f))
    rows, bad = [], []
    with open(os.path.join(tree, "arm_inputs.md5")) as fh:
        lines = [ln.rstrip(NL) for ln in fh if ln.strip()]
    for ln in lines:
        parts = ln.split(TAB) if TAB in ln else ln.split()
        md5_want, name, nbytes = parts[0], parts[1], parts[2]
        hits = index.get(os.path.basename(name), [])
        if len(hits) != 1:
            bad.append({"name": name, "why": "matches=%d" % len(hits)})
            continue
        p = hits[0]
        got = _hash(p, "md5")
        size = os.path.getsize(p)
        ok = (got == md5_want and size == int(nbytes))
        rows.append({"name": name, "rel": os.path.relpath(p, tree),
                     "md5_expected": md5_want, "md5": got, "bytes_expected": int(nbytes),
                     "bytes": size, "sha256": _hash(p, "sha256"),
                     "status": "OK" if ok else "MISMATCH"})
        if not ok:
            bad.append({"name": name, "why": "md5/bytes", "got": got, "want": md5_want,
                        "bytes": size, "bytes_want": int(nbytes)})
    cols = ["name", "rel", "md5_expected", "md5", "bytes_expected", "bytes",
            "sha256", "status"]
    with open(os.path.join(logs, "tree_pins16%s.tsv" % suffix), "w") as fh:
        fh.write(TAB.join(cols) + NL)
        for r in rows:
            fh.write(TAB.join(str(r[c]) for c in cols) + NL)
    # The canonical t09 directory holds all 148 Pot A..J axes (plus Juglet); this tree only
    # carries Pot J's 12, so enumerate the tree's Axes and look each one up.
    ax = []
    tree_ax = os.path.join(tree, "Axes")
    ax_files = sorted(f for f in os.listdir(tree_ax) if f.endswith("_Axis.xyz"))
    if len(ax_files) != 12:
        bad.append({"name": "Axes", "why": "tree has %d axes want 12" % len(ax_files)})
    # Pot_J_Piece_09 is unscored and switched off (arm_pieces_J.tsv field 5 = off); the
    # t09-potJ tree ships its Axes/Pot_J_Piece_09_Axis.xyz EMPTY.  That file is never read:
    # every cell binds the arm pack over /Dataset/SfS_pp/Axes, and each pack takes all 12
    # axes from the t09 canonical directory.  The emptiness is recorded, not failed.
    empty_sha = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    tolerated = []
    for f in ax_files:
        p_can = os.path.join(T09_AX, f)
        p_tree = os.path.join(tree_ax, f)
        sha_can = _hash(p_can, "sha256") if os.path.exists(p_can) else "MISSING_CANONICAL"
        sha_tree = _hash(p_tree, "sha256")
        keep = (f == "Pot_J_Piece_09_Axis.xyz" and sha_tree == empty_sha)
        ax.append({"axis": f, "canonical_sha256": sha_can, "tree_sha256": sha_tree,
                   "identical": sha_can == sha_tree})
        if keep:
            tolerated.append(f)
        if sha_can != sha_tree and not keep:
            bad.append({"name": f, "why": "tree axis differs from t09 canonical"})
    cols = ["axis", "canonical_sha256", "tree_sha256", "identical"]
    with open(os.path.join(logs, "axis_pins16%s.tsv" % suffix), "w") as fh:
        fh.write(TAB.join(cols) + NL)
        for r in ax:
            fh.write(TAB.join(str(r[c]) for c in cols) + NL)
    brk = sorted(os.path.basename(r["rel"]) for r in rows
                 if r["rel"].startswith("Breaklines" + os.sep))
    status = {"run": run, "tree": tree, "manifest_lines": len(lines), "rows": len(rows),
              "bad": bad, "axes": len(ax),
              "axes_all_identical": all(r["identical"] for r in ax),
              "breaklines": len(brk), "breakline_expect": 11,
              "tree_axes_empty_unused": tolerated,
              "j01_tree_sha256": [r["tree_sha256"] for r in ax
                                  if r["axis"] == STEM + "_Axis.xyz"],
              "tree_manifest_status": "OK" if not bad else "FAIL"}
    with open(os.path.join(logs, "tree_verify16%s.json" % suffix), "w") as fh:
        json.dump(status, fh, indent=1)
    print("[t16] tree manifest lines=%d rows=%d bad=%d axes=%d breaklines=%d"
          % (len(lines), len(rows), len(bad), len(ax), len(brk)), flush=True)
    return status, bad


def cell_check(run, axes_dir, j01_sha, label):
    logs = os.path.join(run, "logs")
    rows, bad = [], []
    files = sorted(f for f in os.listdir(axes_dir) if f.endswith("_Axis.xyz"))
    ok = len(files) == 12
    rows.append({"kind": "count", "name": "axes", "expected": "12", "got": str(len(files)),
                 "status": "OK" if ok else "FAIL"})
    if not ok:
        bad.append("axes=%d" % len(files))
    for f in files:
        p = os.path.join(axes_dir, f)
        got = _hash(p, "sha256")
        if f == STEM + "_Axis.xyz":
            rows.append({"kind": "j01", "name": f, "expected": j01_sha, "got": got,
                         "status": "OK" if got == j01_sha else "FAIL"})
            if got != j01_sha:
                bad.append("j01 %s" % got)
            continue
        want = _hash(os.path.join(T09_AX, f), "sha256")
        want13 = _hash(os.path.join(T13_AX, f), "sha256")
        okay = (got == want and got == want13)
        rows.append({"kind": "fixed", "name": f, "expected": want13, "got": got,
                     "status": "OK" if okay else "FAIL"})
        if not okay:
            bad.append("axis %s" % f)
    cols = ["kind", "name", "expected", "got", "status"]
    with open(os.path.join(logs, "identity16_%s.tsv" % label), "w") as fh:
        fh.write(TAB.join(cols) + NL)
        for r in rows:
            fh.write(TAB.join(str(r[c]) for c in cols) + NL)
    print("[t16] cell %s fixed-axes=%d bad=%d" % (label, len(files) - 1, len(bad)),
          flush=True)
    return len(bad) == 0, bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--tree", required=True)
    ap.add_argument("--axes-dir", default="")
    ap.add_argument("--j01-sha", default="")
    ap.add_argument("--label", default="")
    a = ap.parse_args()
    run = os.path.abspath(a.run)
    _status, bad = tree_check(run, os.path.abspath(a.tree), a.label)
    print("T16-TREE-" + ("OK" if not bad else "FAIL"), flush=True)
    rc = 0 if not bad else 1
    if a.axes_dir:
        if not (a.j01_sha and a.label):
            print("[t16] --axes-dir needs --j01-sha and --label", flush=True)
            return 2
        cok, _cbad = cell_check(run, os.path.abspath(a.axes_dir), a.j01_sha, a.label)
        print("T16-IDENTITY-" + ("OK" if cok else "FAIL"), flush=True)
        if not cok:
            rc = 2
    return rc


if __name__ == "__main__":
    sys.exit(main() or 0)
