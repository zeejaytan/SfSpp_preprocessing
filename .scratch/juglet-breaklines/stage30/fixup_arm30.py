#!/usr/bin/env python3
"""ticket 30 -- repair an arm run's tables from the files the run kept.

Job 33868514 (arm 1, Pot A at theta=3.4) wrote three tables that the fixed instruments
now write correctly:

  1. armcells30.tsv  -- the tag and scheme columns are EMPTY (submit_30_arm.sbatch.tmpl did
     not export IXTAG, so run_arm30.sh got no tag argument) and break0_segs holds
     ".PCD" because the PCD parser took the file-format comment instead of the segment
     comment. Every other column is the cell's own value.
  2. breaks30.tsv    -- segs/hpts hold ".PCD"/"v0.7" for the same reason.
  3. measure30.tsv   -- measure_pair30.py globbed <root>/<tag>/<pot>/<piece>, which is the
     dump-cell layout; in the arm layout (<root>/<pot>/<piece>) it read the subdirectories
     as pieces, so every row was no_pair and the meta keys shifted.

This script re-reads what the run KEPT -- surfaces/*.ply, breaklines/*.pcd -- and writes
armcells30_v2.tsv, breaks30_v2.tsv, measure30_v2.tsv and FIXUPS-ARM30.txt beside them.
It is read-only with respect to the originals and touches no geometry.

usage: fixup_arm30.py <run_dir>
"""
import sys, os, io, glob

HERE = os.environ.get("M30_DIR") or os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import measure_pair30 as mp


def read_tsv(path):
    head, rows = None, []
    with io.open(path, newline="") as fh:
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if head is None:
                head = f
                continue
            rows.append(f)
    return head, rows


def pcd_head(path):
    """(POINTS, <segs>, <span>) -- the second comment line carries segs and span."""
    pts, com = 0, []
    with io.open(path, newline="") as fh:
        for line in fh:
            s = line.rstrip("\n")
            if s.startswith("POINTS "):
                pts = int(s.split()[1])
            elif s.startswith("#"):
                com.append(s)
            elif s.startswith("DATA"):
                break
    segs = span = 0
    if len(com) >= 2:
        f = com[1].split()
        if len(f) >= 3:
            segs, span = int(f[1]), int(f[2])
    return pts, segs, span


def xyz_lines(pcd):
    p = pcd[:-4] + ".xyz"
    if not os.path.isfile(p):
        return 0
    n = 0
    with io.open(p, newline="") as fh:
        for _ in fh:
            n += 1
    return n


def main(argv):
    if len(argv) < 2:
        print("usage: fixup_arm30.py <run_dir>")
        return 2
    run = argv[1].rstrip("/")
    tag = os.path.basename(run).split("_", 2)[-1]
    arms = os.path.join(run, "out", "arms")
    head, rows = read_tsv(os.path.join(arms, "armcells30.tsv"))
    n_tag = n_scheme = n_seg = 0
    v2 = []
    for f in rows:
        r = dict(zip(head, f))
        if not r.get("tag"):
            r["tag"] = tag
            n_tag += 1
        if not r.get("scheme"):
            r["scheme"] = "theta" + r.get("theta", "")
            n_scheme += 1
        pcd = os.path.join(arms, r.get("pot", ""), r.get("piece", ""), "breaklines",
                           r.get("piece", "") + "_Breakline_0.pcd")
        if os.path.isfile(pcd):
            _pts, segs, _span = pcd_head(pcd)
            if str(segs) != r.get("break0_segs"):
                r["break0_segs"] = str(segs)
                n_seg += 1
        v2.append([r.get(c, "") for c in head])
    dest_cells = os.path.join(arms, "armcells30_v2.tsv")
    with io.open(dest_cells, "w", newline="\n") as fh:
        fh.write("\t".join(head) + "\n")
        for row in v2:
            fh.write("\t".join(row) + "\n")

    bh = ["tag", "pot", "piece", "breakline", "file", "points", "segs", "span", "xyz_lines"]
    brows = []
    for pcd in sorted(glob.glob(os.path.join(arms, "*", "*", "breaklines", "*_Breakline_*.pcd"))):
        cell = os.path.dirname(os.path.dirname(pcd))
        pot, piece = os.path.basename(os.path.dirname(cell)), os.path.basename(cell)
        b = os.path.basename(pcd)
        k = b.rsplit("_Breakline_", 1)[-1].replace(".pcd", "")
        pts, segs, span = pcd_head(pcd)
        brows.append([tag, pot, piece, k, b, str(pts), str(segs), str(span), str(xyz_lines(pcd))])
    dest_breaks = os.path.join(arms, "breaks30_v2.tsv")
    with io.open(dest_breaks, "w", newline="\n") as fh:
        fh.write("\t".join(bh) + "\n")
        for row in brows:
            fh.write("\t".join(row) + "\n")

    meta = mp.cell_meta(dest_cells)
    cols = ["role", "tag", "scheme", "pot", "piece", "status", "n0", "n1", "med_nn_mm",
            "med_along_mm", "p90_along_mm", "max_along_mm", "med_across_mm", "p90_across_mm",
            "max_across_mm", "coincidence_share_1um", "surf0_points_log", "surf1_points_log",
            "count_match"]
    out_rows, n_ok, n_nopair, n_mismatch = [], 0, 0, 0
    for dirpath, dirnames, _files in os.walk(arms):
        if os.path.basename(dirpath) != "surfaces":
            continue
        dirnames[:] = []
        cell = os.path.dirname(dirpath)
        pot, piece = os.path.basename(os.path.dirname(cell)), os.path.basename(cell)
        row = meta.get(("~", pot, piece), {})
        f0 = glob.glob(os.path.join(dirpath, "*_Surface_0.ply"))
        f1 = glob.glob(os.path.join(dirpath, "*_Surface_1.ply"))
        rec = [row.get("role", "?"), row.get("tag", tag), row.get("scheme", ""), pot, piece]
        if not f0 or not f1:
            rec += ["no_pair"] + [""] * 14
            n_nopair += 1
            out_rows.append(rec)
            continue
        try:
            p0, n0 = mp.load_ply(f0[0])
            p1, n1 = mp.load_ply(f1[0])
            if p0.shape[0] < 3 or p1.shape[0] < 3:
                rec += ["degenerate"] + [""] * 14
                out_rows.append(rec)
                continue
            s = mp.pair_stats(p0, n0, p1, n1)
        except Exception as exc:
            rec += ["load_error:" + str(exc).replace("\t", " ")] + [""] * 14
            out_rows.append(rec)
            continue
        l0, l1 = row.get("surf0_points", ""), row.get("surf1_points", "")
        match = ""
        if l0.isdigit() and l1.isdigit():
            match = "yes" if (int(l0) == s["n0"] and int(l1) == s["n1"]) else "no"
            if match == "no":
                n_mismatch += 1
        rec += ["ok", str(s["n0"]), str(s["n1"]),
                "%.6f" % s["med_nn_mm"], "%.6f" % s["med_along_mm"], "%.6f" % s["p90_along_mm"],
                "%.6f" % s["max_along_mm"], "%.6f" % s["med_across_mm"], "%.6f" % s["p90_across_mm"],
                "%.6f" % s["max_across_mm"], "%.6f" % s["coincidence_share_1um"],
                l0, l1, match]
        n_ok += 1
        out_rows.append(rec)
    out_rows.sort(key=lambda r: (r[3], r[4]))
    dest_measure = os.path.join(arms, "measure30_v2.tsv")
    with io.open(dest_measure, "w", newline="\n") as fh:
        fh.write("\t".join(cols) + "\n")
        for row in out_rows:
            fh.write("\t".join(row) + "\n")

    with io.open(os.path.join(arms, "FIXUPS-ARM30.txt"), "w", newline="\n") as fh:
        fh.write("ticket 30 -- arm tables repaired from the files this run kept\n")
        fh.write("run: %s\n" % run)
        fh.write("arm tag recovered from the run directory name: %s\n" % tag)
        fh.write("armcells30_v2.tsv : tag filled on %d rows, scheme filled on %d, break0_segs recounted on %d\n"
                 % (n_tag, n_scheme, n_seg))
        fh.write("breaks30_v2.tsv  : rebuilt from every breaklines/*_Breakline_*.pcd; "
                 "segs and span come from the SECOND comment line, not the format line\n")
        fh.write("measure30_v2.tsv : %d cells, %d with a pair, %d without, count_match=no on %d\n"
                 % (len(out_rows), n_ok, n_nopair, n_mismatch))
        fh.write("originals armcells30.tsv / breaks30.tsv / measure30.tsv are untouched\n")
        fh.write("ran on %s (SLURM_JOB_ID=%s); read-only post-processing of kept files, no geometry, no pipeline\n"
                 % (os.uname()[1], os.environ.get("SLURM_JOB_ID", "none")))
    print("[FIXUP-ARM30] %s tag=%s cells=%d pair=%d nopair=%d mismatch=%d -> armcells30_v2.tsv breaks30_v2.tsv measure30_v2.tsv"
          % (os.path.basename(run), tag, len(out_rows), n_ok, n_nopair, n_mismatch))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

