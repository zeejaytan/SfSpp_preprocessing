#!/usr/bin/env python3
"""stage01.py -- stage Ticket 01 axis directories, scripts and hash records.

Four directories of 31 Pot E axis files are staged from the archived Ticket 19 packs:
OWN and AUTHOR are byte copies of $T19/axes/{OWN,AUTHOR}; OWN_E27_AUTHOR starts from
the OWN pack and takes only Pot_E_Piece_27_Axis.xyz from AUTHOR; AUTHOR_E27_OWN is its
reciprocal.  Nothing is rebuilt and no axis byte is rewritten: every staged file is a
copy whose sha256 is checked against the file it came from, and every arm is checked to
differ from its background at exactly one path.

Run on the login node (file copies and hashes only).
"""
import argparse
import hashlib
import json
import os
import shutil
import sys

WANT_SHA = "0ba6d10fa6885a67a92a92bb37ec7c138f25f32622368bfcafb5bfae3fa637c9"
E27 = "Pot_E_Piece_27_Axis.xyz"
E28 = "Pot_E_Piece_28_Axis.xyz"
NPOT = 31
SCRIPTS = ("cell01.sbatch", "submit.sbatch", "measure01.sbatch", "report01.sbatch",
           "surface01.py", "report01.py")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def axis_files(d):
    return sorted(f for f in os.listdir(d)
                  if f.startswith("Pot_E_") and f.endswith("_Axis.xyz"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t19", required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--src", required=True, help="worktree .scratch/surface-parity/t01")
    a = ap.parse_args()
    t19, run, src = a.t19, a.run, a.src

    exe = os.path.join(t19, "work", "t19", "build", "Hierarchy-T19")
    if not os.path.isfile(exe):
        sys.exit("stage01: no executable %s" % exe)
    got = sha(exe)
    if got != WANT_SHA:
        sys.exit("stage01: executable sha %s != %s" % (got, WANT_SHA))
    for d in ("axes", "logs", "out", "score", "evidence", "renders", "work/t01"):
        os.makedirs(os.path.join(run, d), exist_ok=True)
    for d in ("Axes", "Breaklines", "Ground Truth", "Mesh", "Result", "Surfaces"):
        os.makedirs(os.path.join(run, "mount", d), exist_ok=True)
    with open(os.path.join(run, "logs", "exe.sha"), "w") as f:
        f.write(WANT_SHA + "\n")
    with open(os.path.join(run, "logs", "executable.sha256"), "w") as f:
        f.write("%s  %s\n" % (WANT_SHA, exe))

    base = {arm: os.path.join(t19, "axes", arm) for arm in ("OWN", "AUTHOR")}
    for arm, d in base.items():
        n = len(axis_files(d))
        if n != NPOT:
            sys.exit("stage01: %s has %d axis files" % (d, n))
    plan = {"OWN": ("OWN", None), "AUTHOR": ("AUTHOR", None),
            "OWN_E27_AUTHOR": ("OWN", "AUTHOR"),
            "AUTHOR_E27_OWN": ("AUTHOR", "OWN")}
    rows, swaps = [], []
    hashes = {}
    for arm in ("OWN", "AUTHOR", "OWN_E27_AUTHOR", "AUTHOR_E27_OWN"):
        bg, donor = plan[arm]
        out = os.path.join(run, "axes", arm)
        os.makedirs(out, exist_ok=True)
        hashes[arm] = {}
        for name in axis_files(base[bg]):
            dst = os.path.join(out, name)
            shutil.copyfile(os.path.join(base[bg], name), dst)
            want = sha(os.path.join(base[bg], name))
            got = sha(dst)
            if got != want:
                sys.exit("stage01: copy mismatch %s %s" % (arm, name))
            used = "background:%s" % bg
            if donor and name == E27:
                shutil.copyfile(os.path.join(base[donor], name), dst)
                want = sha(os.path.join(base[donor], name))
                got = sha(dst)
                if got != want:
                    sys.exit("stage01: donor copy mismatch %s %s" % (arm, name))
                used = "donor:%s" % donor
            hashes[arm][name] = got
            bgh = sha(os.path.join(base[bg], name))  # the background file's own hash
            rows.append((arm, name, got, bgh, used,
                         os.path.join(base[bg], name) if used.startswith("background") else os.path.join(base[donor], name)))
        names = sorted(os.listdir(out))
        if len(names) != NPOT:
            sys.exit("stage01: %s staged %d files" % (arm, len(names)))
        diff = [n for n in names if hashes[arm][n] != hashes[bg][n]]
        want_diff = [] if donor is None else [E27]
        if sorted(diff) != sorted(want_diff):
            sys.exit("stage01: %s differs from %s at %s, expected %s"
                     % (arm, bg, diff, want_diff))
        if donor is not None and hashes[arm][E28] != hashes[bg][E28]:
            sys.exit("stage01: %s moved E28 bytes" % arm)
    own27 = hashes["OWN"][E27]
    auth27 = hashes["AUTHOR"][E27]
    if own27 == auth27:
        sys.exit("stage01: E27 donor bytes identical (%s); redundant swaps" % own27)
    for arm in ("OWN", "AUTHOR", "OWN_E27_AUTHOR", "AUTHOR_E27_OWN"):
        swaps.append((arm, "27", own27, auth27, hashes[arm][E27], E28, hashes[arm][E28]))

    for name in SCRIPTS:
        s = os.path.join(src, name)
        if os.path.isfile(s):
            shutil.copyfile(s, os.path.join(run, "work", "t01", name))
    with open(os.path.join(run, "logs", "axes_manifest.tsv"), "w") as f:
        f.write("arm\tfile\tsha256\tbackground_sha256\tsource\tsource_path\n")
        for r in rows:
            f.write("\t".join(r) + "\n")
    with open(os.path.join(run, "logs", "axes_swap.tsv"), "w") as f:
        f.write("arm\tpiece\town_sha256\tauthor_sha256\tfinal_sha256\t"
                "e28_final_sha256\tbackground\n")
        for arm, piece, o, au, fin, _, e28 in swaps:
            f.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n"
                    % (arm, piece, o, au, fin, e28, plan[arm][0]))
    with open(os.path.join(run, "logs", "stage.json"), "w") as f:
        json.dump({"run": os.path.basename(run), "executable_sha256": WANT_SHA,
                   "axis_dir_sha256": {arm: hashes[arm] for arm in hashes},
                   "e27_own": own27, "e27_author": auth27,
                   "note": "axes staged byte-for-byte from T19/axes"},
                  f, indent=2, sort_keys=True)
    print("STAGE-OK axes=4 files=%d e27_own=%s e27_author=%s"
          % (sum(len(v) for v in hashes.values()), own27[:12], auth27[:12]))


if __name__ == "__main__":
    main()
