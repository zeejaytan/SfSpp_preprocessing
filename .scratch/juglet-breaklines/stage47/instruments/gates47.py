#!/usr/bin/env python3
# ticket 47 gates -- frame, density, spacing; freeze-manifest rows.
# Frame gate: the new cloud must sit where the mesh vertices sit (~700 mm scan-pose
# frame, the frame the GT transforms were derived in).  A real -GLOBAL_SHIFT AUTO
# recentering is a thousands-of-mm constant offset, so: max|coord| < 5000 mm,
# |center-mesh_center| <= 2 mm/axis, |extent-mesh_extent| <= 2 mm/axis, first-3-rows
# distance to the nearest mesh vertex <= 1.0 mm; the old dump (mesh vertices copied
# out) must match the mesh extent exactly.  Density gate: sampled 999k-1005k, kept
# 800k-900k (Pot A 01: 1000088 -> 843433), ratio 0.78-0.90, normals in FIELDS.
# Exit 0 = all gates pass on all nine; 1 = any FAIL; 2 = parse trouble.
import argparse, hashlib, json, math, os, sys
import numpy as np
from scipy.spatial import cKDTree

SEED = 47  # spacing column of the manifest must be reproducible


def md5_of(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def read_obj(path):
    verts, faces = [], []
    with open(path, 'r', errors='replace') as f:
        for line in f:
            if line.startswith('v '):
                p = line.split()
                verts.append((float(p[1]), float(p[2]), float(p[3])))
            elif line.startswith('f '):
                idx = []
                for tok in line.split()[1:]:
                    s = tok.split('/')[0]
                    i = int(s)
                    idx.append(i - 1 if i > 0 else len(verts) + i)
                faces.append(idx[:3])
    return np.asarray(verts, dtype=np.float64), faces


def mesh_area(v, faces):
    total = 0.0
    for f in faces:
        a, b, c = v[f[0]], v[f[1]], v[f[2]]
        total += 0.5 * float(np.linalg.norm(np.cross(b - a, c - a)))
    return total


def read_pcd(path, first_n=3):
    header, first = {}, []
    n = 0
    mins = np.full(3, np.inf)
    maxs = np.full(3, -np.inf)
    sums = np.zeros(3)
    maxabs = 0.0
    in_data = False
    with open(path, 'r', errors='replace') as f:
        for line in f:
            if not in_data:
                if line.startswith('DATA'):
                    header['DATA'] = line.split()[1]
                    in_data = True
                else:
                    parts = line.split()
                    if parts:
                        header[parts[0]] = parts[1:]
                continue
            parts = line.split()
            if len(parts) < 3:
                continue
            try:
                x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
            except ValueError:
                continue
            p = np.array([x, y, z])
            if len(first) < first_n:
                first.append(p)
            mins = np.minimum(mins, p)
            maxs = np.maximum(maxs, p)
            sums += p
            maxabs = max(maxabs, float(np.abs(p).max()))
            n += 1
    ext = maxs - mins if n else np.zeros(3)
    ctr = sums / n if n else np.zeros(3)
    return header, first, n, mins, maxs, ext, ctr, maxabs


def load_pcd_points(path, cap=None):
    pts = []
    in_data = False
    with open(path, 'r', errors='replace') as f:
        for line in f:
            if not in_data:
                if line.startswith('DATA'):
                    in_data = True
                continue
            parts = line.split()
            if len(parts) < 3:
                continue
            try:
                pts.append((float(parts[0]), float(parts[1]), float(parts[2])))
            except ValueError:
                continue
            if cap and len(pts) >= cap:
                break
    return np.asarray(pts, dtype=np.float64)


def read_gt_translation(path):
    rows = []
    with open(path, 'r', errors='replace') as f:
        for line in f:
            vals = [t for t in line.replace(chr(13), '').split() if t]
            if len(vals) >= 4:
                rows.append([float(x) for x in vals[:4]])
    if len(rows) < 3:
        return None
    return (rows[0][3], rows[1][3], rows[2][3])


def parse_cc_log(path):
    out = {'sampled': None, 'final': None, 'shift_lines': [], 'status': None}
    with open(path, 'r', errors='replace') as f:
        for line in f:
            if 'Sampled cloud created:' in line:
                for tok in line.replace(':', ' ').split():
                    if tok.isdigit():
                        out['sampled'] = int(tok)
            elif 'Final Point Count:' in line:
                for tok in line.replace(':', ' ').split():
                    if tok.isdigit():
                        out['final'] = int(tok)
            elif 'Global Shift' in line or 'GLOBAL_SHIFT' in line:
                out['shift_lines'].append(line.strip())
            elif line.startswith('Status:'):
                out['status'] = line.split(':', 1)[1].strip()
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ds', required=True)
    ap.add_argument('--staging', required=True)
    ap.add_argument('--old-dir', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--command', default='')
    ap.add_argument('--date', default='')
    args = ap.parse_args()

    T = chr(9)
    pieces = ['Juglet_Piece_' + str(n) for n in range(1, 10)]
    gate_rows, manifest_rows, detail = [], [], {}
    rc = 0

    hdr = T.join(['piece', 'sampled', 'kept', 'ratio', 'normals_ok', 'spacing_mm',
                  'mesh_verts', 'mesh_area_mm2', 'old_points', 'maxabs_new', 'maxabs_mesh',
                  'center_delta_mm', 'extent_delta_mm', 'first3_maxdist_mm',
                  'gt_translation_mm', 'shift_lines', 'frame_pass', 'density_pass', 'note'])
    man_hdr = T.join(['piece', 'source_mesh', 'mesh_md5', 'sampled_points', 'kept_points',
                      'pcd_md5', 'pcd_bytes', 'cc_log', 'log_md5', 'spacing_mm', 'date', 'command'])

    for piece in pieces:
        mesh = args.ds + '/Mesh/Juglet/' + piece + '_Mesh.obj'
        pcd = args.staging + '/' + piece + '_Point.pcd'
        log = args.staging + '/' + piece + '_cc.log'
        old = args.old_dir + '/' + piece + '_Point.pcd'
        gt = args.ds + '/Juglet_GT/' + piece + '_T.txt'
        note = []

        v, faces = read_obj(mesh)
        area = mesh_area(v, faces)
        m_mins, m_maxs = v.min(axis=0), v.max(axis=0)
        m_ext = m_maxs - m_mins
        m_ctr = (m_mins + m_maxs) / 2.0

        header, first, n, mins, maxs, ext, ctr, maxabs = read_pcd(pcd)
        _, _, on, _, _, o_ext, _, _ = read_pcd(old)
        cc = parse_cc_log(log)
        gt_t = read_gt_translation(gt)

        fields = header.get('FIELDS', [])
        normals_ok = all(f in fields for f in ('normal_x', 'normal_y', 'normal_z'))
        kept = n
        sampled = cc['sampled'] if cc['sampled'] is not None else kept
        ratio = (kept / sampled) if sampled else 0.0

        center_delta = float(np.abs(ctr - m_ctr).max())
        extent_delta = float(np.abs(ext - m_ext).max())
        old_ext_delta = float(np.abs(o_ext - m_ext).max())
        tree = cKDTree(v)
        first3 = float(max(tree.query(p)[0] for p in first)) if first else math.inf
        maxabs_ok = maxabs < 5000.0
        frame_pass = (maxabs_ok and center_delta <= 2.0 and extent_delta <= 2.0
                      and first3 <= 1.0 and old_ext_delta <= 0.01)
        if not maxabs_ok:
            note.append('maxabs ' + format(maxabs, '.1f') + ' looks shifted')
        if center_delta > 2.0:
            note.append('center delta ' + format(center_delta, '.3f') + ' mm')
        if extent_delta > 2.0:
            note.append('extent delta ' + format(extent_delta, '.3f') + ' mm')
        if first3 > 1.0:
            note.append('first rows ' + format(first3, '.3f') + ' mm off mesh')
        if old_ext_delta > 0.01:
            note.append('old dump extent off mesh by ' + format(old_ext_delta, '.4f'))

        density_pass = (normals_ok and 999000 <= sampled <= 1005000
                        and 800000 <= kept <= 900000 and 0.78 <= ratio <= 0.90
                        and kept >= 10000)
        if not normals_ok:
            note.append('normals missing from FIELDS')
        if not (800000 <= kept <= 900000):
            note.append('kept ' + str(kept) + ' outside corpus band')

        rng = np.random.default_rng(SEED)
        pts = load_pcd_points(pcd)
        if len(pts) > 250000:
            sub = pts[rng.choice(len(pts), 250000, replace=False)]
        else:
            sub = pts
        stree = cKDTree(sub)
        d, _ = stree.query(sub, k=2)
        spacing = float(np.median(d[:, 1]))

        cmd = args.command.replace('{mesh}', mesh).replace('{staging}', args.staging)
        gate_rows.append(T.join([
            piece, str(sampled), str(kept), format(ratio, '.4f'), str(int(normals_ok)),
            format(spacing, '.4f'), str(len(v)), format(area, '.1f'), str(on),
            format(maxabs, '.1f'), format(float(np.abs(v).max()), '.1f'),
            format(center_delta, '.3f'), format(extent_delta, '.3f'), format(first3, '.3f'),
            (';'.join(format(t, '.2f') for t in gt_t) if gt_t else 'n/a'),
            ('; '.join(cc['shift_lines']) or 'none'),
            str(int(frame_pass)), str(int(density_pass)),
            ('; '.join(note) if note else 'ok')]))
        manifest_rows.append(T.join([
            piece, mesh, md5_of(mesh), str(sampled), str(kept), md5_of(pcd),
            str(os.path.getsize(pcd)), log, md5_of(log), format(spacing, '.4f'),
            args.date, cmd]))
        detail[piece] = {'sampled': sampled, 'kept': kept, 'ratio': round(ratio, 4),
                         'spacing_mm': round(spacing, 4), 'area_mm2': round(area, 1),
                         'frame_pass': bool(frame_pass), 'density_pass': bool(density_pass),
                         'maxabs': round(maxabs, 1), 'center_delta_mm': round(center_delta, 3),
                         'extent_delta_mm': round(extent_delta, 3),
                         'first3_maxdist_mm': round(first3, 3),
                         'gt_translation_mm': ([round(t, 2) for t in gt_t] if gt_t else None),
                         'shift_lines': cc['shift_lines'], 'old_points': on,
                         'mesh_verts': len(v)}
        if not (frame_pass and density_pass):
            rc = 1

    with open(args.out + '/gates47.tsv', 'w') as f:
        f.write(hdr + chr(10))
        f.write(chr(10).join(gate_rows) + chr(10))
    with open(args.out + '/manifest_rows.tsv', 'w') as f:
        f.write('# MANIFEST_JUGLET_CC -- one unseeded CloudCompare draw per piece, frozen (ticket 47).' + chr(10))
        f.write('# spacing = median NN distance on a seeded (seed 47) 250k subsample, mm.' + chr(10))
        f.write(man_hdr + chr(10))
        f.write(chr(10).join(manifest_rows) + chr(10))
    with open(args.out + '/gates47_detail.json', 'w') as f:
        json.dump(detail, f, indent=2, sort_keys=True)

    print(hdr)
    for r in gate_rows:
        print(r)
    npass = sum(1 for p in pieces if detail[p]['frame_pass'] and detail[p]['density_pass'])
    print('[gates47] rc=' + str(rc) + ' (' + str(npass) + '/9 pass both gates)')
    return rc


if __name__ == '__main__':
    sys.exit(main())
