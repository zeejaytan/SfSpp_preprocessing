#!/usr/bin/env python3
"""stage305.py -- ticket 305 Stage 3: per-pot, per-arm assembler input trees.

    stage305.py --pot B --corpus CORP --lanes LANES --axes OURS \
                --out TREES --arms OO,MO,OM,MM --named 9 --np 9

O = authors' released input, M = ours.  (Breaklines, Axes) = arm name.
  OO  corpus Breaklines/<stem>_Breakline_0.pcd + corpus Axes
  MO  lanes/<stem>.Bl0                        + corpus Axes
  OM  corpus Breakline_0                      + axes305/<stem>_Axis.xyz
  MM  lanes/<stem>.Bl0                        + axes305/<stem>_Axis.xyz

A piece is ELIGIBLE for an arm only when every input it needs exists and is
non-empty.  Ineligible pieces get a ZERO-BYTE Axes/<stem>_Axis.xyz, which the
untouched shim turns into shard_on_off=false (main_pristine_batch.cpp:69-73),
so the arm's denominators count only what it actually had.

Files shared by all arms (Mesh, Surfaces, Ground Truth) are hardlinked from the
frozen corpus; Breaklines and Axes are per-arm copies.
"""
import argparse
import hashlib
import os
import shutil


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def link(s, t):
    if os.path.exists(t):
        os.remove(t)
    try:
        os.link(s, t)
    except OSError:
        shutil.copyfile(s, t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pot", required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--lanes", default="")
    ap.add_argument("--axes", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--arms", default="OO,MO,OM,MM")
    ap.add_argument("--named", type=int, required=True,
                    help="highest piece index the pot's data_path.h block names")
    ap.add_argument("--np", type=int, required=True, help="SHARD_NUMBER")
    ap.add_argument("--copy-shared", type=int, default=0,
                    help="1 = copy Mesh/Surfaces instead of hardlinking them")
    a = ap.parse_args()
    P = a.pot
    arms = [x.strip() for x in a.arms.split(",") if x.strip()]
    subdirs = ("Breaklines", "Surfaces", "Mesh", "Axes", "Ground Truth")
    gt = os.path.join(a.corpus, "Ground Truth")
    graph = os.path.join(gt, "Pot_%s_simple_graph.txt" % P)
    if not os.path.isfile(graph):
        raise SystemExit("missing graph " + graph)

    rows = []
    for arm in arms:
        bl_src = "O" if arm[0] == "O" else "M"
        ax_src = "O" if arm[1] == "O" else "M"
        T = os.path.join(a.out, P, arm)
        for d in subdirs:
            os.makedirs(os.path.join(T, d), exist_ok=True)
        n_on = 0
        for p in range(1, a.named + 1):
            stem = "Pot_%s_Piece_%02d" % (P, p)
            reasons = []
            tgt = os.path.join(gt, "Pot_%s_Piece_%d_T.txt" % (P, p))
            if not os.path.isfile(tgt):
                reasons.append("no_gt_T")
            bl = (os.path.join(a.corpus, "Breaklines", stem + "_Breakline_0.pcd")
                  if bl_src == "O" else os.path.join(a.lanes, stem + ".Bl0"))
            if not (os.path.isfile(bl) and os.path.getsize(bl) > 0):
                reasons.append("no_breakline")
            ax = (os.path.join(a.corpus, "Axes", stem + "_Axis.xyz")
                  if ax_src == "O" else os.path.join(a.axes, stem + "_Axis.xyz"))
            if not (os.path.isfile(ax) and os.path.getsize(ax) > 0):
                reasons.append("no_axis")
            # pots A,B ship <stem>_Mesh.obj; pots C..J ship <stem>_Mesh_DS.obj, and the
            # data_path.h block names that same suffix -- but the tree we stage always uses
            # the block's name, which is what the assembler reads.
            mesh = ""
            for suf in ("_Mesh_DS.obj", "_Mesh.obj"):
                cand = os.path.join(a.corpus, "Mesh", stem + suf)
                if os.path.isfile(cand):
                    mesh = cand
                    mesh_name = stem + suf
                    break
            else:
                mesh_name = stem + "_Mesh.obj"
            s0 = os.path.join(a.corpus, "Surfaces", stem + "_Surface_0.xyz")
            s1 = os.path.join(a.corpus, "Surfaces", stem + "_Surface_1.xyz")
            for f in (mesh, s0, s1):
                if not (f and os.path.isfile(f)):
                    reasons.append("no_mesh" if f == "" else
                                   "no_" + os.path.basename(f).split("_")[-1])
            if reasons:
                # zero-byte axis file = shard_on_off false, and nothing else staged
                open(os.path.join(T, "Axes", stem + "_Axis.xyz"), "w").close()
                rows.append((P, arm, p, stem, "off", ";".join(reasons)))
                continue
            link(bl, os.path.join(T, "Breaklines", stem + "_Breakline_0.pcd"))
            if ax_src == "O":
                link(ax, os.path.join(T, "Axes", stem + "_Axis.xyz"))
            else:
                shutil.copyfile(ax, os.path.join(T, "Axes", stem + "_Axis.xyz"))
            for f, d, nm in ((mesh, "Mesh", mesh_name), (s0, "Surfaces", None),
                             (s1, "Surfaces", None)):
                dst = os.path.join(T, d, nm or os.path.basename(f))
                if a.copy_shared:
                    shutil.copyfile(f, dst)
                else:
                    link(f, dst)
            shutil.copyfile(tgt, os.path.join(T, "Ground Truth",
                                              os.path.basename(tgt)))
            n_on += 1
            rows.append((P, arm, p, stem, "on", ""))
        link(graph, os.path.join(T, "Ground Truth", os.path.basename(graph)))
        # manifest of the arm's staged inputs
        with open(os.path.join(T, "arm_inputs.md5"), "w") as fh:
            for d in subdirs:
                dd = os.path.join(T, d)
                for fn in sorted(os.listdir(dd)):
                    fp = os.path.join(dd, fn)
                    fh.write("%s\t%s\t%d\n" % (md5(fp), fn, os.path.getsize(fp)))
        print("ARM %s %s: %d/%d pieces on" % (P, arm, n_on, a.named), flush=True)
        if n_on == 0:
            print("!!!! arm %s has no pieces on" % arm)

    tsv = os.path.join(a.out, "arm_pieces_%s.tsv" % P)
    with open(tsv, "w") as fh:
        fh.write("pot\tarm\tpiece\tstem\ton_off\treason\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print("wrote", tsv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
