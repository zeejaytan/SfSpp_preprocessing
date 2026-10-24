#!/usr/bin/env python3
"""Ticket 290 Phase 1 - is the frozen input corpus complete, unchanged and readable?

Checks, against the corpus's own manifests:
  * every released cloud still has the md5, byte size and point count the manifest recorded;
  * every derived cloud likewise (its manifest carries the source mesh md5 as well);
  * every piece of the scored corpus (148, from ticket 284's phase0-table.tsv) has exactly one
    <Piece>_Point.pcd under Point/<Pot>/, and no cloud in the folder is unaccounted for;
  * which clouds are ascii and which are binary, and what FIELDS each class declares.

Read-only. Writes nothing. Exit 0 when every check passes, 1 otherwise.
"""
import concurrent.futures as cf
import hashlib
import os
import sys

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Point"
MAN_R = os.path.join(CORPUS, "MANIFEST_released.tsv")
MAN_D = os.path.join(CORPUS, "MANIFEST_derived.tsv")
TABLE = "/data/gpfs/projects/punim2657/SfSpp/runs/20261024-1851_ee5f4dc_p284-rescore/phase0-table.tsv"


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            b = f.read(1 << 22)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def header(path):
    """PCD header as (dict of keyword -> rest-of-line, byte offset of the DATA line)."""
    out = {}
    with open(path, "rb") as f:
        blob = f.read(8192)
    off = 0
    for raw in blob.split(b"\n"):
        line = raw.decode("ascii", "replace").strip()
        off += len(raw) + 1
        if not line or line.startswith("#"):
            continue
        key, _, rest = line.partition(" ")
        out[key.upper()] = rest
        if key.upper() == "DATA":
            break
    return out


def rows(path):
    with open(path) as f:
        head = f.readline().rstrip("\n").split("\t")
        for line in f:
            line = line.rstrip("\n")
            if line:
                yield dict(zip(head, line.split("\t")))


def main():
    bad = 0

    # ---- the 143 released clouds -------------------------------------------------
    rel = list(rows(MAN_R))
    paths = {}
    for r in rel:
        paths[r["piece"]] = os.path.join(CORPUS, r["pot"], r["piece"] + "_Point.pcd")
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        got = dict(zip([r["piece"] for r in rel], ex.map(md5, [paths[r["piece"]] for r in rel])))
    md5_bad, pts_bad, size_bad = [], [], []
    for r in rel:
        p = paths[r["piece"]]
        if not os.path.isfile(p):
            md5_bad.append((r["piece"], "MISSING"))
            continue
        if got[r["piece"]] != r["md5"]:
            md5_bad.append((r["piece"], got[r["piece"]] + " != " + r["md5"]))
        h = header(p)
        if int(h["POINTS"]) != int(r["points"]):
            pts_bad.append((r["piece"], h["POINTS"] + " != " + r["points"]))
        if os.path.getsize(p) != int(r["bytes"]):
            size_bad.append((r["piece"], str(os.path.getsize(p)) + " != " + r["bytes"]))
    print("[INV] released rows=%d md5_mismatch=%d points_mismatch=%d bytes_mismatch=%d"
          % (len(rel), len(md5_bad), len(pts_bad), len(size_bad)))
    print("[INV] released md5 sample: %s=%s (header_ok=%s)"
          % (rel[0]["piece"], rel[0]["md5"], rel[0]["header_ok"]))
    for row in md5_bad + pts_bad + size_bad:
        print("  [FAIL] %s %s" % row)
    bad += len(md5_bad) + len(pts_bad) + len(size_bad)

    # ---- the 5 derived clouds ----------------------------------------------------
    der = list(rows(MAN_D))
    dpaths = [os.path.join(CORPUS, r["piece"].split("_Piece_")[0], r["piece"] + "_Point.pcd") for r in der]
    with cf.ThreadPoolExecutor(max_workers=5) as ex:
        dgot = list(ex.map(md5, dpaths))
    d_bad = []
    for r, p, m in zip(der, dpaths, dgot):
        if not os.path.isfile(p):
            d_bad.append((r["piece"], "MISSING"))
            continue
        if m != r["pcd_md5"]:
            d_bad.append((r["piece"], "md5 " + m + " != " + r["pcd_md5"]))
        if int(header(p)["POINTS"]) != int(r["points"]):
            d_bad.append((r["piece"], "points " + header(p)["POINTS"] + " != " + r["points"]))
        if os.path.getsize(p) != int(r["bytes"]):
            d_bad.append((r["piece"], "bytes mismatch"))
        if md5(r["source_mesh"]) != r["mesh_md5"]:
            d_bad.append((r["piece"], "source mesh md5 changed"))
    print("[INV] derived rows=%d mismatch=%d" % (len(der), len(d_bad)))
    for row in d_bad:
        print("  [FAIL] %s %s" % row)
    bad += len(d_bad)

    # ---- coverage of the scored corpus ------------------------------------------
    table = list(rows(TABLE))
    want = {}
    for r in table:
        name = "%s_Piece_%s" % (r["pot"], r["piece"])
        want.setdefault(name, 0)
        want[name] += 1
    have = {}
    for pot in sorted(os.listdir(CORPUS)):
        d = os.path.join(CORPUS, pot)
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            if f.endswith("_Point.pcd"):
                have.setdefault(f[: -len("_Point.pcd")], []).append(pot)
    missing = [p for p in want if p not in have]
    dupes = {p: v for p, v in have.items() if len(v) > 1}
    extra = [p for p in have if p not in want]
    no_row_but_file = [p for p in have if p not in want]
    print("[INV] scored_corpus rows=%d pieces=%d files=%d missing=%d duplicated=%d unaccounted=%d"
          % (len(table), len(want), sum(len(v) for v in have.values()), len(missing), len(dupes), len(extra)))
    for p in missing:
        print("  [FAIL] missing cloud for %s" % p)
    for p, v in dupes.items():
        print("  [FAIL] %s appears in %s" % (p, v))
    for p in no_row_but_file:
        print("  [FAIL] cloud %s has no row in phase0-table.tsv" % p)
    bad += len(missing) + len(dupes) + len(extra)

    # per pot, so the tally is checkable against the ticket's A8 B9 C4 D29 E31 F6 G7 H11 I27 J11
    tally = {}
    for p, v in have.items():
        tally.setdefault(v[0], 0)
        tally[v[0]] += 1
    print("[INV] per pot: " + " ".join("%s=%d" % (k, tally[k]) for k in sorted(tally)))

    # ---- ascii vs binary, and the field order both classes declare --------------
    enc, fields = {}, {}
    for p, v in sorted(have.items()):
        path = os.path.join(CORPUS, v[0], p + "_Point.pcd")
        h = header(path)
        enc[h.get("DATA", "?").split()[0]] = enc.get(h.get("DATA", "?").split()[0], 0) + 1
        fields.setdefault(h.get("DATA", "?").split()[0], h.get("FIELDS", "?"))
    print("[INV] encoding: " + " ".join("%s=%d" % kv for kv in sorted(enc.items())))
    for k in sorted(fields):
        print("[INV] FIELDS (%s): %s" % (k, fields[k]))
    print("[INV] VERDICT " + ("PASS" if bad == 0 else "FAIL %d problem(s)" % bad))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
