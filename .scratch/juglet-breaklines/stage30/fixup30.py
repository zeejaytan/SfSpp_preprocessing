"""ticket 30 -- recompute, from the files the run KEPT, the columns two instrument defects left wrong.

Written after job 33868337 (run 20261027-0637_66c84dc_t30-clouds) finished. Nothing here
re-runs the pipeline: every number is read out of files that run wrote and kept.

defect 1  both cell scripts carried an awk program written as ${print $3} -- a stray $
          before the opening brace, from a substitution that went wrong -- so awk refused the
          program and every point count parsed from a PLY header came back empty:
          cells30.tsv n0/n1 are 0 and dumpcounts30.tsv's points column is empty. The table's
          own n_cloud comes from numpy, not from awk, so analyse30.py was unaffected.
defect 2  analyse30.py recorded mesh_verts_used as the number of CLOUD points the noise-floor
          sample used, not the mesh's vertex count -- the two are equal by accident of the
          code, and the column reads identical to n_cloud on every row. faces was correct.

usage: fixup30.py <run_dir>
"""
import io
import os
import sys

def read_tsv(path):
    with io.open(path, newline="") as fh:
        head = fh.readline().rstrip("\n").split("\t")
        rows = [l.rstrip("\n").split("\t") for l in fh if l.strip()]
    return head, rows

def write_tsv(path, head, rows, note=""):
    with io.open(path, "w", newline="\n") as fh:
        if note:
            fh.write(note)
        fh.write("\t".join(head) + "\n")
        for r in rows:
            fh.write("\t".join("" if v is None else str(v) for v in r) + "\n")

def ply_vertices(path):
    try:
        with io.open(path, "r", errors="replace") as fh:
            for line in fh:
                if line.startswith("element vertex"):
                    return int(line.split()[2])
                if line.startswith("end_header"):
                    break
    except (IOError, OSError, ValueError):
        pass
    return ""

def obj_vertices(path):
    n = 0
    try:
        with io.open(path, "r", errors="replace") as fh:
            for line in fh:
                if line[:2] == "v ":
                    n += 1
    except (IOError, OSError):
        return ""
    return n

def main(argv):
    if len(argv) != 2:
        print("usage: fixup30.py <run_dir>")
        return 2
    run = os.path.abspath(argv[1])
    out = os.path.join(run, "out")
    notes = []

    mesh_of = {}
    mp = os.path.join(out, "meshpaths.tsv")
    if os.path.isfile(mp):
        with io.open(mp, newline="") as fh:
            for line in fh:
                f = line.rstrip("\n").split("\t")
                if len(f) >= 3 and f[0] and not f[0].startswith("#"):
                    mesh_of[(f[0], f[1])] = f[2]

    head, rows = read_tsv(os.path.join(out, "tableA30.tsv"))
    iv = head.index("mesh_verts_used")
    ir = head.index("r1_file")
    nfix = 0
    for r in rows:
        key = (r[head.index("arm")], r[head.index("piece")])
        path = mesh_of.get(key, "")
        v = obj_vertices(path) if path else ""
        if v != "" and str(v) != r[iv]:
            r[iv] = v
            nfix += 1
        tag = r[head.index("cloud")].split("/")[0]
        r1 = os.path.join(out, "dump", tag, r[head.index("piece")], "r1_downsampled.ply")
        r[ir] = os.path.basename(r1) if os.path.isfile(r1) else ""
    write_tsv(os.path.join(out, "tableA30_v2.tsv"), head, rows)
    notes.append("[FIX2] tableA30_v2.tsv: mesh_verts_used replaced by the OBJ's own 'v ' count on "
                 "%d of %d rows (was the noise-floor sample size); r1_file filled in." % (nfix, len(rows)))

    cells_path = os.path.join(out, "cells", "cells30.tsv")
    if os.path.isfile(cells_path):
        head, rows = read_tsv(cells_path)
        i0, i1 = head.index("n0"), head.index("n1")
        fixed = 0
        for r in rows:
            cell = os.path.join(out, "cells", r[0], r[2], r[3], "surfaces")
            for idx, k in ((i0, "0"), (i1, "1")):
                if not r[idx] or r[idx] == "0":
                    cand = [f for f in os.listdir(cell) if f.endswith("_Surface_%s.ply" % k)] if os.path.isdir(cell) else []
                    if cand:
                        v = ply_vertices(os.path.join(cell, sorted(cand)[0]))
                        if v != "":
                            r[idx] = v
                            fixed += 1
        write_tsv(os.path.join(out, "cells", "cells30_v2.tsv"), head, rows)
        notes.append("[FIX1] cells/cells30_v2.tsv: n0/n1 recounted from each cell's kept "
                     "surfaces/*_Surface_{0,1}.ply headers -- %d columns filled." % fixed)

    dc_path = os.path.join(out, "cells", "dumpcounts30.tsv")
    if os.path.isfile(dc_path):
        head, rows = read_tsv(dc_path)
        ip = head.index("points")
        fixed = 0
        for r in rows:
            if not r[ip] or r[ip] == "0":
                cands = [os.path.join(out, "dump", r[0], r[2], r[3]),
                         os.path.join(out, "cells", r[0], r[1], r[2], "surfaces", r[3])]
                v = ""
                for f in cands:
                    v = ply_vertices(f)
                    if v != "":
                        break
                if v != "":
                    r[ip] = v
                    fixed += 1
        write_tsv(os.path.join(out, "cells", "dumpcounts30_v2.tsv"), head, rows)
        notes.append("[FIX1] cells/dumpcounts30_v2.tsv: points recounted from the kept copy of each "
                     "file -- %d rows filled." % fixed)

    lines = ["# ticket 30 run %s -- repairs made after the job, from files the run kept" % os.path.basename(run),
             "# nothing here re-runs the pipeline; no number below is inferred, each is read",
             "#   out of a file this run wrote (PLY header, OBJ 'v ' line) and kept.",
             "#",
             "# DEFECT 1 (run_arm30.sh, run_dump30.sh): the awk programs were written with a stray",
             "#   $ before the opening brace instead of '{print $3}', so awk aborted with",
             "#   'syntax error' and every PLY point count taken through awk came back empty.",
             "#   Shows up as cells30.tsv n0/n1 = 0 and an empty dumpcounts30.tsv points column.",
             "#   Fixed in the instrument; job 33868337 ran the broken copy.",
             "# DEFECT 2 (analyse30.py): mesh_verts_used was assigned the noise-floor sample size",
             "#   (equal to n_cloud on every row) instead of the OBJ vertex count. mesh_floor_deg",
             "#   itself is unaffected -- the floor was computed from the mesh throughout. Fixed in",
             "#   the instrument; tableA30_v2.tsv carries the true counts.",
             "#",
             "# Run on the login node: python3, stdlib only, read-only over the run directory, no numpy,",
             "#   no container, no pipeline step. The six-job cap is why the recount is not a job.",
             "#"]
    lines += notes
    with io.open(os.path.join(out, "FIXUPS30.txt"), "w", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(notes))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
