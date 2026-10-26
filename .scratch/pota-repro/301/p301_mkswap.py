#!/usr/bin/env python3
"""Ticket 301 -- write ONE piece's staged axis file with the direction its own reference pose implies.

Input  : the frozen corpus axis file of that piece (read only, never written).
Output : a REAL file in the run dataset's SfS_pp/Axes/, plus a provenance JSON.

What changes: the direction triple (fields 4-6) of every axis line. Everything else -- the axis point
in fields 1-3, the line count, the field order, any trailing fields -- is written back unchanged, which
is the ticket's Phase 0 requirement "keep the rest of the file's content intact".

Why every line: a multi-axis piece makes the matcher try every axis (class/feature_matching.cpp:1481,
:1551-1552), so leaving one bad candidate in place would let the run pick it and the experiment would
not test the axis at all. Each line keeps its own sign: the released files carry no consistent sign
convention (15 of 21 single-axis Pot D pieces project negatively onto the pot axis at |dot| ~ 1.0), and
AxisAlignment (class/reconstruction.cpp:66) builds its frame from the signed direction, so flipping a
sign would change the frame convention as well as the direction.

The direction written is   +/-  R_GT^T . a_world   with R_GT the piece's released rotation and a_world
the pot axis reconstructed exactly as ticket 299 section 6 did (see p301_axis.py beside this file and
the values in p301-constants.json).

Stdlib only: this runs on a compute node.
"""
import argparse, hashlib, json, math, os, sys


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_axis_like_loader(path):
    """BreakLine::ReadAxis (class/data_structure.cpp:142) is a stream of doubles, six per line:
    x y z nx ny nz, read with a plain formatted extractor until EOF. Emulate exactly that."""
    toks = open(path).read().split()
    lines, i = [], 0
    while i + 6 <= len(toks):
        lines.append([float(x) for x in toks[i:i + 6]])
        i += 6
    return lines


def unit(v):
    n = math.sqrt(sum(c * c for c in v))
    return [c / n for c in v]


def ang(u, v):
    """Angle between two directions, minimised over the two signs (an axis is a line, not a vector)."""
    d = abs(sum(a * b for a, b in zip(unit(u), unit(v))))
    return math.degrees(math.acos(min(1.0, d)))


def read_T(path):
    rows = [l.split() for l in open(path) if l.strip()]
    M = [[0.0] * 4 for _ in range(4)]
    for i in range(min(3, len(rows) - 1)):     # Trans::Read takes num-1 rows (class/data_structure.cpp:648)
        M[i] = [float(x) for x in rows[i][:4]]
    M[3][3] = 1.0
    return M


def rot(M, v):
    return [sum(M[i][j] * v[j] for j in range(3)) for i in range(3)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--constants", required=True)
    ap.add_argument("--piece", type=int, required=True)
    ap.add_argument("--corpus-axis", required=True)
    ap.add_argument("--gt", required=True, help="the piece's staged Ground Truth transform")
    ap.add_argument("--out", required=True, help="staged axis file to write")
    ap.add_argument("--provenance", required=True)
    a = ap.parse_args()

    C = json.load(open(a.constants))
    p = str(a.piece)
    if p not in C["swaps"]:
        sys.exit("FATAL piece %s is not a swap target in %s" % (p, a.constants))
    sw = C["swaps"][p]

    corpus_md5 = md5(a.corpus_axis)
    if corpus_md5 != sw["axis_md5"]:
        sys.exit("FATAL corpus axis md5 %s != recorded %s for piece %s -- refusing to swap from bytes "
                 "the ticket did not measure" % (corpus_md5, sw["axis_md5"], p))
    if os.path.islink(a.out):
        sys.exit("FATAL %s is a symlink; the swapped axis must be a real file" % a.out)

    src_lines = [l.rstrip() for l in open(a.corpus_axis) if l.strip()]
    if len(src_lines) != sw["n_lines"]:
        sys.exit("FATAL %d lines in %s, constants recorded %d"
                 % (len(src_lines), a.corpus_axis, sw["n_lines"]))

    out_lines = []
    for k, line in enumerate(src_lines):
        tok = line.split()
        if len(tok) < 6:
            sys.exit("FATAL line %d of %s has %d fields, the loader needs 6" % (k, a.corpus_axis, len(tok)))
        d_new = sw["lines"][k]["d_new"]
        out_lines.append(" ".join(tok[0:3] + ["%.15g" % c for c in d_new] + tok[6:]))
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        f.write("\n".join(out_lines) + "\n")
    staged_md5 = md5(a.out)

    got = read_axis_like_loader(a.out)
    if len(got) != len(src_lines):
        sys.exit("FATAL readback of %s returned %d lines, wrote %d" % (a.out, len(got), len(src_lines)))
    R = read_T(a.gt)
    a_world = C["a_world"]

    lines = []
    for k, v in enumerate(got):
        d = v[3:6]
        dw = rot(R, d)
        rec = dict(
            line=k,
            staged_dir=[float("%.15g" % c) for c in unit(d)],
            planted_dir=sw["lines"][k]["d_new"],
            corpus_dir=sw["lines"][k]["d_corpus"],
            angle_staged_vs_planted_deg=round(ang(d, sw["lines"][k]["d_new"]), 9),
            angle_staged_in_world_vs_a_world_deg=round(ang(dw, a_world), 9),
            angle_staged_vs_corpus_deg=round(ang(d, sw["lines"][k]["d_corpus"]), 6),
        )
        lines.append(rec)
        if rec["angle_staged_vs_planted_deg"] > 1.0:
            sys.exit("FATAL staged direction of line %d reads back %.3f deg from what was planted"
                     % (k, rec["angle_staged_vs_planted_deg"]))

    prov = dict(
        piece=a.piece,
        target_axis_path_in_container="/Dataset/SfS_pp/Axes/%s" % os.path.basename(a.out),
        staged_axis_path=a.out,
        corpus_axis_path=a.corpus_axis,
        corpus_axis_md5=corpus_md5,
        staged_axis_md5=staged_md5,
        staged_is_real_file=(not os.path.islink(a.out)),
        gt_path=a.gt,
        gt_md5=md5(a.gt),
        a_world=a_world,
        a_world_construction="299 section 6 (SVD over R_GT_i @ d_i, single-axis pieces); see p301_axis.py",
        d_pose_implied=sw["d_pose_implied"],
        swaps=lines,
        max_angle_staged_vs_planted_deg=max(l["angle_staged_vs_planted_deg"] for l in lines),
        checker="p301_mkswap.py, parsing the staged file with the loader's own field order",
    )
    json.dump(prov, open(a.provenance, "w"), indent=1)
    print("[SWAP] piece %d  corpus %s -> staged %s" % (a.piece, corpus_md5, staged_md5))
    for l in lines:
        print("[SWAP]  line %d: staged-vs-planted %.2e deg | R_GT.d_staged vs a_world %.2e deg | "
              "moved %.2f deg from the corpus line"
              % (l["line"], l["angle_staged_vs_planted_deg"],
                 l["angle_staged_in_world_vs_a_world_deg"], l["angle_staged_vs_corpus_deg"]))


if __name__ == "__main__":
    main()
