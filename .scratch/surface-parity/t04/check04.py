"""Ticket 04 public evidence validation.

Reads only the run's evidence tables, the run's axis files and the frozen inputs the
tables name; checks the partitions, the trio hashes, the retention of every unmatched or
invalid row, the archive gate, the axis rows and the fixtures.  Prints one line per check,
exits 1 if any check fails.  Writes nothing.
"""

import argparse
import hashlib
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SHIP = "/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship"
T19 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261124-0443_21446b8_t19-decisions"
IMPL = os.path.join(SHIP, "work", "impl_t03")
os.environ.setdefault("SFS_IMPL", IMPL)
for p in (HERE, os.path.join(SHIP, "work"), IMPL, os.path.join(IMPL, "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

import t03_lib as dl      # noqa: E402
import normals04 as nm    # noqa: E402

STEMS = [("Pot_E_Piece_27", 27), ("Pot_E_Piece_28", 28)]
ARMS = ["OWN", "AUTHOR", "OWN_SHAM", "AUTHOR_SHAM",
        "OWN_AUTHOR_NORMALS", "AUTHOR_OWN_NORMALS"]
TRANSFERS = ("OWN_AUTHOR_NORMALS", "AUTHOR_OWN_NORMALS")
NATIVES = ("OWN", "AUTHOR")
SHAMS = ("OWN_SHAM", "AUTHOR_SHAM")
ARCHIVE = {"OWN": "OWN", "AUTHOR": "AUTHOR", "OWN_SHAM": "OWN", "AUTHOR_SHAM": "AUTHOR"}
NATIVE_OF = {"OWN_SHAM": "OWN", "OWN_AUTHOR_NORMALS": "OWN",
             "AUTHOR_SHAM": "AUTHOR", "AUTHOR_OWN_NORMALS": "AUTHOR"}

FAILS = []


def check(name, cond, detail=""):
    if cond:
        print("PASS %s" % name)
    else:
        print("FAIL %s %s" % (name, detail))
        FAILS.append(name)
    return bool(cond)


def read_tsv(path):
    with open(path) as fh:
        lines = [ln.rstrip("\n") for ln in fh if ln.strip()]
    head = lines[0].split("\t")
    rows = [dict(zip(head, ln.split("\t"))) for ln in lines[1:]]
    return head, rows


def sha_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def is_hex64(s):
    return len(s) == 64 and all(c in "0123456789abcdef" for c in s)


def read_axis_rows(path):
    rows = []
    for line in open(path):
        c = line.split()
        if len(c) < 6:
            continue
        rows.append(np.array([float(x) for x in c[:6]], dtype=float))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--expect-terminal", action="store_true")
    a = ap.parse_args()
    run = os.path.abspath(a.run)
    ev = os.path.join(run, "evidence")
    outd = os.path.join(run, "out", "axes04")

    # ---------------------------------------------------------------- inputs.tsv
    head, rows = read_tsv(os.path.join(ev, "inputs.tsv"))
    want = ["sherd", "arm", "face", "points", "xyz_sha256", "normals_sha256",
            "matched", "changed", "invalid_target", "unmatched", "source_sha256"]
    check("inputs.header", head == want, repr(head))
    check("inputs.rows24", len(rows) == 24, str(len(rows)))
    keys = {(int(r["sherd"]), r["arm"], int(r["face"])) for r in rows}
    check("inputs.grid", len(keys) == 24 and
          keys == {(s, ar, f) for _, s in STEMS for ar in ARMS for f in (0, 1)}, str(len(keys)))
    bad = []
    for r in rows:
        p = int(r["points"])
        m, c = int(r["matched"]), int(r["changed"])
        inv, un = int(r["invalid_target"]), int(r["unmatched"])
        if p <= 0 or not is_hex64(r["xyz_sha256"]) or not is_hex64(r["normals_sha256"]):
            bad.append(("fields", r["sherd"], r["arm"], r["face"]))
        if r["arm"] in NATIVES + SHAMS:
            if m or c or inv or un:
                bad.append(("native_counts", r["sherd"], r["arm"], r["face"], m, c, inv, un))
        elif m + inv + un != p or c > m or c < 0:
            bad.append(("partition", r["sherd"], r["arm"], r["face"], m, inv, un, p, c))

    check("inputs.partitions", not bad, str(bad[:4]))

    # ---------------------------------------------------------------- walls vs table
    walls = {}
    for stem, sid in STEMS:
        o0, o1, _ = dl.walls(stem, "own")
        a0, a1, _ = dl.walls(stem, "authors")
        walls[(sid, "own")] = (o0, o1)
        walls[(sid, "authors")] = (a0, a1)
    bad = []
    for r in rows:
        sid, arm, face = int(r["sherd"]), r["arm"], int(r["face"])
        src = "authors" if arm in ("AUTHOR", "AUTHOR_SHAM", "AUTHOR_OWN_NORMALS") else "own"
        w = walls[(sid, src)][face]
        if int(r["points"]) != w.shape[1]:
            bad.append(("points", sid, arm, face, r["points"], w.shape[1]))
        if r["xyz_sha256"] != nm.matrix_sha(w[0:3].T):
            bad.append(("xyz_sha_vs_native", sid, arm, face))
        if arm in NATIVES + SHAMS and r["normals_sha256"] != nm.matrix_sha(w[3:6].T):
            bad.append(("normals_sha_vs_native", sid, arm, face))
        if arm in ("OWN", "OWN_SHAM", "OWN_AUTHOR_NORMALS") and \
                r["source_sha256"] != sha_file(os.path.join(dl.OWN["E"], "Pot_E_Piece_%d.S%d" % (sid, face))):
            bad.append(("source_sha", sid, arm, face))
    check("inputs.walls", not bad, str(bad[:4]))

    # ---------------------------------------------------------------- trio identity
    idx = {(int(r["sherd"]), r["arm"], int(r["face"])): r for r in rows}
    bad = []
    for _, sid in STEMS:
        for f in (0, 1):
            if not (idx[(sid, "OWN", f)]["xyz_sha256"] ==
                    idx[(sid, "OWN_SHAM", f)]["xyz_sha256"] ==
                    idx[(sid, "OWN_AUTHOR_NORMALS", f)]["xyz_sha256"]):
                bad.append(("own_xyz_trio", sid, f))
            if not (idx[(sid, "AUTHOR", f)]["xyz_sha256"] ==
                    idx[(sid, "AUTHOR_SHAM", f)]["xyz_sha256"] ==
                    idx[(sid, "AUTHOR_OWN_NORMALS", f)]["xyz_sha256"]):
                bad.append(("author_xyz_trio", sid, f))
            if idx[(sid, "OWN", f)]["normals_sha256"] != idx[(sid, "OWN_SHAM", f)]["normals_sha256"]:
                bad.append(("own_sham_normals", sid, f))
            if idx[(sid, "AUTHOR", f)]["normals_sha256"] != idx[(sid, "AUTHOR_SHAM", f)]["normals_sha256"]:
                bad.append(("author_sham_normals", sid, f))
    check("inputs.trios", not bad, str(bad[:4]))

    # ---------------------------------------------------------------- runs.tsv
    rhead, runs = read_tsv(os.path.join(ev, "runs.tsv"))
    need = ["sherd", "arm", "status", "k", "axes_sha256", "archive_ok",
            "effective_stride", "drawn_points"]
    check("runs.header", all(c in rhead for c in need), repr(rhead))
    check("runs.rows12", len(runs) == 12, str(len(runs)))
    check("runs.grid", {(int(r["sherd"]), r["arm"]) for r in runs} ==
          {(s, ar) for _, s in STEMS for ar in ARMS}, str(len(runs)))
    bad = []
    for r in runs:
        sid, arm = int(r["sherd"]), r["arm"]
        stem = "Pot_E_Piece_%d" % sid
        path = os.path.join(outd, stem, "%s_Axis.xyz" % arm)
        k = int(r["k"])
        if not os.path.isfile(path):
            bad.append(("missing_axis", sid, arm))
            continue
        if r["axes_sha256"] != sha_file(path):
            bad.append(("axes_sha", sid, arm))
        rows_f = read_axis_rows(path)
        if len(rows_f) != k:
            bad.append(("k_vs_file", sid, arm, k, len(rows_f)))
        if r["status"] == "ok" and k < 1:
            bad.append(("ok_k0", sid, arm))
        if r["status"] == "no_axis" and (k != 0 or not r["reason"]):
            bad.append(("no_axis", sid, arm, k, r["reason"]))
        if int(r["effective_stride"]) < 1 or int(r["drawn_points"]) < 1:
            bad.append(("stride_drawn", sid, arm))
        if arm in TRANSFERS and r["archive_ok"] != "":
            bad.append(("transfer_archive_blank", sid, arm, r["archive_ok"]))
        if arm in ARCHIVE and r["archive_ok"] not in ("0", "1"):
            bad.append(("archive_ok_field", sid, arm, r["archive_ok"]))
    check("runs.fields", not bad, str(bad[:4]))

    # archive recomputation
    bad = []
    for r in runs:
        if r["arm"] not in ARCHIVE:
            continue
        sid, arm = int(r["sherd"]), r["arm"]
        stem = "Pot_E_Piece_%d" % sid
        path = os.path.join(outd, stem, "%s_Axis.xyz" % arm)
        arch = os.path.join(T19, "axes", ARCHIVE[arm], stem + "_Axis.xyz")
        same = sha_file(path) == sha_file(arch)
        exp_ok = 1 if same else 0
        if not same:
            fa, fb = read_axis_rows(arch), read_axis_rows(path)
            if len(fa) == len(fb) and len(fa) > 0:
                exp_ok = 1 if np.max(np.abs(np.array(fa) - np.array(fb))) <= 1e-9 else 0
        if int(r["archive_ok"]) != exp_ok:
            bad.append(("archive_ok_stale", sid, arm, r["archive_ok"], exp_ok))
        if int(r["archive_rank_count_agree"]) != (1 if len(read_axis_rows(arch)) == len(read_axis_rows(path)) else 0):
            bad.append(("rank_count_agree", sid, arm))
    check("runs.archive", not bad, str(bad[:4]))

    # ---------------------------------------------------------------- axes.tsv
    ahead, arows = read_tsv(os.path.join(ev, "axes.tsv"))
    awant = ["sherd", "arm", "rank", "oriented_deg", "line_deg", "anchor_mm",
             "pos_x", "pos_y", "pos_z", "dir_x", "dir_y", "dir_z", "cost"]
    check("axes.header", ahead == awant, repr(ahead))
    bad = []
    n_by = {}
    for r in arows:
        key = (int(r["sherd"]), r["arm"])
        n_by[key] = n_by.get(key, 0) + 1
        o, l, d = float(r["oriented_deg"]), float(r["line_deg"]), float(r["anchor_mm"])
        comp = np.array([float(r[c]) for c in awant[6:12]])
        if not (0.0 <= o <= 180.0 and 0.0 <= l <= 90.0 and d >= 0.0):
            bad.append(("angle_range", key, r["rank"], o, l, d))
        if abs(l - min(o, 180.0 - o)) > 1e-5:
            bad.append(("line_from_oriented", key, r["rank"], o, l))
        if not np.all(np.isfinite(comp)):
            bad.append(("components", key, r["rank"]))
        stem = "Pot_E_Piece_%d" % key[0]
        f = read_axis_rows(os.path.join(outd, stem, "%s_Axis.xyz" % key[1]))
        rk = int(r["rank"])
        if rk < 1 or rk > len(f):
            bad.append(("rank_missing", key, rk, len(f)))
        else:
            w = f[rk - 1]
            if np.max(np.abs(w - np.r_[comp[0:3], comp[3:6]])) > 1e-12:
                bad.append(("component_vs_file", key, rk))
    check("axes.values", not bad, str(bad[:4]))
    bad = []
    for r in runs:
        key = (int(r["sherd"]), r["arm"])
        if n_by.get(key, 0) != int(r["k"]):
            bad.append(("axes_rows_vs_k", key, n_by.get(key, 0), r["k"]))
    rank_bad = []
    for key in n_by:
        rks = sorted(int(r["rank"]) for r in arows
                     if (int(r["sherd"]), r["arm"]) == key)
        if rks != list(range(1, len(rks) + 1)):
            rank_bad.append((key, rks))
    check("axes.ranks", not bad and not rank_bad, str((bad + rank_bad)[:4]))

    # ---------------------------------------------------------------- retention
    bad = []
    for stem, sid in STEMS:
        for arm in TRANSFERS:
            nat = NATIVE_OF[arm]
            src = "authors" if arm.startswith("AUTHOR") else "own"
            for f in (0, 1):
                z = np.load(os.path.join(ev, "matches", "%s_%s_face%d.npz" % (stem, arm, f)))
                tw = walls[(sid, src)][f]
                dw = walls[(sid, "authors" if src == "own" else "own")][f]
                m, c = z["matched"], z["changed"]
                inv, un = z["invalid_target"], z["unmatched"]
                if not np.array_equal(z["xyz"], tw[0:3].T):
                    bad.append(("npz_xyz", sid, arm, f))
                if not np.array_equal(z["native_normals"], tw[3:6].T):
                    bad.append(("npz_native", sid, arm, f))
                if not (m.sum() + inv.sum() + un.sum() == tw.shape[1] and
                        np.all((m.astype(int) + inv.astype(int) +
                                un.astype(int)) == 1)):
                    bad.append(("npz_partition", sid, arm, f))
                out = z["out_normals"]
                if not np.array_equal(out[~m], tw[3:6].T[~m]):
                    bad.append(("npz_retention", sid, arm, f))
                d = z["donor"][m]
                if d.size and (np.any(d < 0) or np.any(d >= dw.shape[1])):
                    bad.append(("npz_donor_range", sid, arm, f))
                if d.size and not np.array_equal(out[m], dw[3:6].T[d]):
                    bad.append(("npz_donor_normal", sid, arm, f))
                dist = np.linalg.norm(z["xyz"][m] - dw[0:3].T[d], axis=1) if d.size else np.zeros(0)
                if d.size and np.max(np.abs(dist - z["distance"][m])) > 1e-9:
                    bad.append(("npz_distance", sid, arm, f))
                if np.any(z["distance"][m] > nm.CUT_MM + 1e-12):
                    bad.append(("npz_cut", sid, arm, f))
                if not np.array_equal(c, m & np.any(out != tw[3:6].T, axis=1)):
                    bad.append(("npz_changed", sid, arm, f))
                ir = idx[(sid, arm, f)]
                if (int(ir["matched"]), int(ir["changed"]), int(ir["invalid_target"]),
                        int(ir["unmatched"])) != (int(m.sum()), int(c.sum()),
                                                  int(inv.sum()), int(un.sum())):
                    bad.append(("npz_counts_vs_table", sid, arm, f))
    check("matches.retention", not bad, str(bad[:4]))

    # ---------------------------------------------------------------- fixtures / renders / jobs / sources
    fh, fr = read_tsv(os.path.join(ev, "fixtures.tsv"))
    want_f = ["inclusive_cut", "outside_cut", "same_face", "invalid_target",
              "invalid_donor", "tie_first", "duplicates_preserved", "normal_sign",
              "identity_order"]
    check("fixtures.names", [r["name"] for r in fr] == want_f, repr([r["name"] for r in fr]))
    check("fixtures.pass", all(r["status"] == "PASS" for r in fr),
          repr([(r["name"], r["status"]) for r in fr if r["status"] != "PASS"]))

    rh, rr = read_tsv(os.path.join(ev, "renders.tsv"))
    check("renders.header", rh == ["sherd", "path", "scale_bar_mm"], repr(rh))
    check("renders.rows", len(rr) == 2, str(len(rr)))
    bad = []
    for r in rr:
        p = os.path.join(run, r["path"])
        if not os.path.isfile(p) or os.path.getsize(p) < 1000:
            bad.append(("missing_png", r["path"]))
        else:
            with open(p, "rb") as fh_:
                if fh_.read(8) != b"\x89PNG\r\n\x1a\n":
                    bad.append(("png_magic", r["path"]))
        if int(r["scale_bar_mm"]) != 20:
            bad.append(("scale_bar", r["path"], r["scale_bar_mm"]))
    check("renders.files", not bad, str(bad[:4]))

    jh, jr = read_tsv(os.path.join(ev, "jobs.tsv"))
    check("jobs.header", jh == ["job_id", "state", "exit_code"], repr(jh))
    check("jobs.row", len(jr) >= 1 and jr[0]["job_id"].isdigit(), repr(jr[:1]))
    TERMINAL = ("COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "NODE_FAIL",
                "PREEMPTED", "OUT_OF_MEMORY", "BOOT_FAIL", "DEADLINE")
    bad = [r for r in jr if r["state"] in TERMINAL and not r["exit_code"].strip()]
    check("jobs.exit_code", not bad, str(bad[:4]))
    if a.expect_terminal:
        jid = jr[0]["job_id"]
        done = [r for r in jr if r["job_id"] == jid and r["state"] in TERMINAL]
        check("jobs.terminal", bool(done) and all(r["exit_code"].strip() for r in done),
              repr(jr))

    sh, sr = read_tsv(os.path.join(ev, "sources.tsv"))
    check("sources.header", sh == ["kind", "path", "sha256", "bytes", "detail"], repr(sh))
    bad = []
    kinds = {r["kind"] for r in sr}
    if not {"input_wall", "reference", "archive_axis", "code"} <= kinds:
        bad.append(("kinds", sorted(kinds)))
    for r in sr:
        if not os.path.isfile(r["path"]):
            bad.append(("missing_source", r["path"]))
        elif sha_file(r["path"]) != r["sha256"]:
            bad.append(("source_sha", r["path"]))
    check("sources.hashes", not bad, str(bad[:4]))

    print("SUMMARY failures=%d" % len(FAILS))
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(main())
