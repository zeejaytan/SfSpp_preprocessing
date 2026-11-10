
"""geomio.py - loaders for the pota328 geometry bundle (PCL ASCII PLY / PCD v0.7) and GT axes."""
import numpy as np, os

def load_ply(path):
    with open(path, 'r') as f:
        n = 0; props = []
        while True:
            line = f.readline()
            if not line: raise IOError('no end_header in ' + path)
            t = line.split()
            if not t: continue
            if t[0] == 'element' and t[1] == 'vertex': n = int(t[2])
            elif t[0] == 'property': props.append(t[-1])
            elif t[0] == 'end_header': break
        data = np.loadtxt(f, max_rows=n, ndmin=2)
    return data, props

def load_pcd(path):
    hdr = []; n = 0; fields = []
    with open(path, 'r') as f:
        while True:
            line = f.readline()
            if not line: raise IOError('no DATA in ' + path)
            hdr.append(line)
            t = line.split()
            if not t: continue
            if t[0] == 'FIELDS': fields = t[1:]
            elif t[0] == 'POINTS': n = int(t[1])
            elif t[0] == 'DATA':
                if t[1] != 'ascii': raise IOError('only ascii: ' + path)
                break
        data = np.loadtxt(f, max_rows=n, ndmin=2)
    return data, fields, hdr

def load_axis(path):
    a = np.loadtxt(path, ndmin=1).ravel()
    if a.size < 6: raise IOError('axis needs 6 numbers: ' + path)
    c = a[:3]; d = a[3:6]; d = d / np.linalg.norm(d)
    return c, d

def perp_radius(pts, c, d):
    v = pts - c
    return np.linalg.norm(v - np.outer(v @ d, d), axis=1)

def face_stats(pts, nrm, c, d):
    r = perp_radius(pts, c, d)
    return dict(n=pts.shape[0], r_med=float(np.median(r)), r_mean=float(r.mean()),
                r_p10=float(np.percentile(r, 10)), r_p90=float(np.percentile(r, 90)))

def nn_dot(pts_a, nrm_a, pts_b, nrm_b):
    """for each point of a, the dot of its normal with the normal of its nearest b point"""
    from scipy.spatial import cKDTree
    t = cKDTree(pts_b)
    d, j = t.query(pts_a, k=1)
    return d, np.einsum('ij,ij->i', nrm_a, nrm_b[j])
