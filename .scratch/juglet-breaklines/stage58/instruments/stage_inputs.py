#!/usr/bin/env python3
"""stage_inputs.py - ticket 58: build the assembler input trees from the t55 run of record.

The assembler's JUGLET_ORIG block reads /Dataset/SfS_pp/{Breaklines,Surfaces,Mesh,Axes,Ground Truth}.
No Juglet breakline exists anywhere in Dataset/ any more (Dataset/Breaklines holds only Pot_A*),
so the lane files MUST be staged from the t55 run of record, which is READ-ONLY:
  /data/gpfs/projects/punim2657/SfSpp/runs/20261101-2004_05be12c_t55-worness07-breaklines/out/geom

Trees written under <out>/:
  juglet/       Breaklines = t55 Bl0 verbatim; Surfaces = t55 S0/S1 converted from ASC PLY to bare
                6-number .xyz (ReadXYZ at class/data_structure.cpp:781-843 cannot parse a PLY
                header); Mesh, Axes, 'Ground Truth' copied from Dataset/.
  juglet_n60/   identical except every Bl0 lane is arc-length resampled to 60 dots by
                interp_lane.py (the interpolation control). Same Mesh/Axes/Ground Truth.
  pota/         hardlinks (same filesystem, no space cost) of exactly the files the POT_A block
                names, so an arm run never writes Result/ into the shared 4.7G bundle.

Honest note carried into the manifest: interpolating the SAME traced lane raises the dot count
fed to the gate and to CountInlier; it adds no new boundary information.
"""
import argparse, hashlib, os, shutil, subprocess, sys


def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def read_bl0(path):
    lines = open(path, 'r', errors='ignore').read().splitlines()
    nseg = int(lines[1].split()[1])
    dots = []
    started = False
    for ln in lines:
        if not started:
            if ln.startswith('DATA'):
                started = True
            continue
        p = ln.split()
        if len(p) >= 7:
            dots.append(p[:7])
    return nseg, lines, dots


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
    ap.add_argument('--t55', required=True)
    ap.add_argument('--dataset', required=True)
    ap.add_argument('--pota', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--interp-dots', type=int, default=60)
    ap.add_argument('--interp-tool', default=None)
    a = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    tool = a.interp_tool or os.path.join(here, 'interp_lane.py')
    py = sys.executable

    man = []
    for tree in ('juglet', 'juglet_n60'):
        T = os.path.join(a.out, tree)
        for d in ('Breaklines', 'Surfaces', 'Mesh', 'Axes', 'Ground Truth'):
            os.makedirs(os.path.join(T, d), exist_ok=True)
    P = os.path.join(a.out, 'pota')
    for d in ('Breaklines', 'Surfaces', 'Mesh', 'Axes', 'Ground Truth'):
        os.makedirs(os.path.join(P, d), exist_ok=True)

    for i in range(1, 10):
        stem = 'Juglet_Piece_%d' % i
        src_bl0 = os.path.join(a.t55, stem + '.Bl0')
        nseg, lines, dots = read_bl0(src_bl0)
        # juglet: verbatim lane
        shutil.copyfile(src_bl0, os.path.join(a.out, 'juglet', 'Breaklines', stem + '_Breakline_0.pcd'))
        # juglet_n60: resampled lane
        dst60 = os.path.join(a.out, 'juglet_n60', 'Breaklines', stem + '_Breakline_0.pcd')
        r = subprocess.run([py, tool, src_bl0, dst60, str(a.interp_dots)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit('interp failed for %s: %s' % (stem, r.stderr))
        man.append(r.stdout.strip())
        for k in ('0', '1'):
            src = os.path.join(a.t55, '%s.S%s' % (stem, k))
            nv = ply_to_xyz(src, os.path.join(a.out, 'juglet', 'Surfaces',
                                              stem + '_Surface_%s.xyz' % k))
            nv2 = ply_to_xyz(src, os.path.join(a.out, 'juglet_n60', 'Surfaces',
                                               stem + '_Surface_%s.xyz' % k))
            man.append('SURF %s S%s verts=%d' % (stem, k, nv))
            assert nv == nv2
        for tree in ('juglet', 'juglet_n60'):
            shutil.copyfile(os.path.join(a.dataset, 'Mesh', 'Juglet', stem + '_Mesh.obj'),
                            os.path.join(a.out, tree, 'Mesh', stem + '_Mesh.obj'))
            shutil.copyfile(os.path.join(a.dataset, 'Axes', 'Juglet', stem + '_Axis.xyz'),
                            os.path.join(a.out, tree, 'Axes', stem + '_Axis.xyz'))
            shutil.copyfile(os.path.join(a.dataset, 'Juglet_GT', stem + '_T.txt'),
                            os.path.join(a.out, tree, 'Ground Truth', stem + '_T.txt'))
        for tree in ('juglet', 'juglet_n60'):
            shutil.copyfile(os.path.join(a.dataset, 'Juglet_GT', 'Juglet_simple_graph.txt'),
                            os.path.join(a.out, tree, 'Ground Truth', 'Juglet_simple_graph.txt'))
        man.append('LANE %s nseg=%d bl0_dots=%d md5=%s' % (stem, nseg, len(dots), md5(src_bl0)))

    # ---- Pot A staging by hardlink -----------------------------------------
    for i in range(1, 9):
        d2 = '%02d' % i
        for rel, name in (
            ('Breaklines', 'Pot_A_Piece_%s_Breakline_0.pcd' % d2),
            ('Mesh', 'Pot_A_Piece_%s_Mesh.obj' % d2),
            ('Axes', 'Pot_A_Piece_%s_Axis.xyz' % d2),
            ('Surfaces', 'Pot_A_Piece_%s_Surface_0.xyz' % d2),
            ('Surfaces', 'Pot_A_Piece_%s_Surface_1.xyz' % d2),
        ):
            s = os.path.join(a.pota, rel, name)
            t = os.path.join(P, rel, name)
            if not os.path.exists(s):
                raise SystemExit('missing Pot A input: ' + s)
            if os.path.exists(t):
                os.remove(t)
            try:
                os.link(s, t)
            except OSError:
                shutil.copyfile(s, t)
        s = os.path.join(a.pota, 'Ground Truth', 'Pot_A_Piece_%d_T.txt' % i)
        t = os.path.join(P, 'Ground Truth', 'Pot_A_Piece_%d_T.txt' % i)
        if os.path.exists(t):
            os.remove(t)
        os.link(s, t)
    os.link(os.path.join(a.pota, 'Ground Truth', 'Pot_A_simple_graph.txt'),
            os.path.join(P, 'Ground Truth', 'Pot_A_simple_graph.txt'))

    with open(os.path.join(a.out, 'stage_manifest.txt'), 'w') as fh:
        fh.write('\n'.join(man) + '\n')
    print('\n'.join(man))
    print('STAGE OK', a.out)


if __name__ == '__main__':
    main()
