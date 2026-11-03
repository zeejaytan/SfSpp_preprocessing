#!/usr/bin/env python3
"""stage69_inputs.py -- ticket 69: assembler input tree from a ticket-69 edgeline cell.

Same shape as t68's stage67_inputs.py, but the lanes AND the surfaces come from the cell's
out/geom (so the tree carries the lanes that cell actually traced), and the pot, mesh dir and
ground-truth dir are explicit.

  Breaklines/<P>_Breakline_0.pcd   = geom/<P>.Bl0  (interior line; the assembler reads only _0)
  Surfaces/<P>_Surface_{0,1}.xyz   = geom/<P>.S{0,1} converted from ASCII PLY to bare 6-number
                                     .xyz (ReadXYZ at class/data_structure.cpp:781-843 cannot
                                     parse a PLY header)
  Mesh/<P>_Mesh.obj                = --mesh-dir (corpus Mesh/ is FLAT; Dataset/Mesh/<pot> is not)
  Axes/<P>_Axis.xyz                = --axis-dir, the released axis (flat corpus Axes/)
  Ground Truth/<P>_T.txt           = --gt-dir, the authors' pose; plus <pot>_simple_graph.txt
"""
import argparse, os, shutil


def ply_to_xyz(src, dst, want=6):
    n = None
    hdr_end = None
    with open(src, 'r', errors='ignore') as fh:
        lines = fh.read().splitlines()
    for i, ln in enumerate(lines):
        s = ln.split()
        if len(s) >= 3 and s[0] == 'element' and s[1] == 'vertex':
            n = int(s[2])
        if ln.strip() == 'end_header':
            hdr_end = i
            break
    if n is None or hdr_end is None:
        raise SystemExit('not an ascii PLY: ' + src)
    body = lines[hdr_end + 1: hdr_end + 1 + n]
    with open(dst, 'w') as fh:
        for ln in body:
            p = ln.split()
            fh.write(' '.join(p[:want]) + '\n')
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--geom', required=True)
    ap.add_argument('--pot', required=True)
    ap.add_argument('--pieces', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--mesh-dir', required=True)
    ap.add_argument('--axis-dir', required=True)
    ap.add_argument('--gt-dir', required=True)
    ap.add_argument('--gt-graph', default=None)
    ap.add_argument('--surfaces-dir', default=None,
                    help='take <P>_Surface_{0,1}.xyz from here instead of converting the cell PLY '
                         '(the corpus surfaces are what the seating control used, so a lane-only '
                         'arm varies the lanes alone)')
    a = ap.parse_args()

    T = a.out
    for d in ('Breaklines', 'Surfaces', 'Mesh', 'Axes', 'Ground Truth'):
        os.makedirs(os.path.join(T, d), exist_ok=True)

    man = []
    for P in a.pieces.split():
        bl = os.path.join(a.geom, P + '.Bl0')
        if not os.path.isfile(bl):
            raise SystemExit('missing lane: ' + bl)
        shutil.copyfile(bl, os.path.join(T, 'Breaklines', P + '_Breakline_0.pcd'))
        for k in ('0', '1'):
            dst = os.path.join(T, 'Surfaces', '%s_Surface_%s.xyz' % (P, k))
            if a.surfaces_dir:
                src = os.path.join(a.surfaces_dir, '%s_Surface_%s.xyz' % (P, k))
                if not os.path.isfile(src):
                    raise SystemExit('missing corpus surface: ' + src)
                shutil.copyfile(src, dst)
                man.append('SURF %s S%s from=%s' % (P, k, src))
                continue
            src = os.path.join(a.geom, '%s.S%s' % (P, k))
            if not os.path.isfile(src):
                raise SystemExit('missing surface: ' + src)
            nv = ply_to_xyz(src, dst)
            man.append('SURF %s S%s verts=%d' % (P, k, nv))
        mesh = None
        for cand in (os.path.join(a.mesh_dir, P + '_Mesh.obj'),
                     os.path.join(a.mesh_dir, P + '_Mesh_DS.obj')):
            if os.path.isfile(cand):
                mesh = cand
                break
        if mesh is None:
            raise SystemExit('missing mesh for ' + P + ' under ' + a.mesh_dir)
        shutil.copyfile(mesh, os.path.join(T, 'Mesh', P + '_Mesh.obj'))
        ax = os.path.join(a.axis_dir, P + '_Axis.xyz')
        if not os.path.isfile(ax):
            raise SystemExit('missing axis: ' + ax)
        shutil.copyfile(ax, os.path.join(T, 'Axes', P + '_Axis.xyz'))
        n = int(P.split('_')[-1])
        gt = None
        for cand in (os.path.join(a.gt_dir, '%s_T.txt' % P),
                     os.path.join(a.gt_dir, '%s_Piece_%d_T.txt' % (a.pot, n)),
                     os.path.join(a.gt_dir, '%s_Piece_%02d_T.txt' % (a.pot, n))):
            if os.path.isfile(cand):
                gt = cand
                break
        if gt is None:
            raise SystemExit('missing ground truth for ' + P + ' under ' + a.gt_dir)
        shutil.copyfile(gt, os.path.join(T, 'Ground Truth', os.path.basename(gt)))
        man.append('LANE %s mesh=%s gt=%s' % (P, os.path.basename(mesh), os.path.basename(gt)))

    if a.gt_graph and os.path.isfile(a.gt_graph):
        shutil.copyfile(a.gt_graph, os.path.join(T, 'Ground Truth', os.path.basename(a.gt_graph)))
    with open(os.path.join(T, 'stage69_manifest.txt'), 'w') as fh:
        fh.write('\n'.join(man) + '\n')
    print('\n'.join(man))
    print('STAGE69 OK', T)


if __name__ == '__main__':
    main()
