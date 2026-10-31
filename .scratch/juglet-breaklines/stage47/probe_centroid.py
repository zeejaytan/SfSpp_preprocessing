import sys
import numpy as np

def obj_mesh(path):
    verts = []
    faces = []
    with open(path) as f:
        for line in f:
            if line.startswith('v '):
                p = line.split()
                verts.append([float(p[1]), float(p[2]), float(p[3])])
            elif line.startswith('f '):
                idx = [int(t.split('/')[0]) - 1 for t in line.split()[1:]]
                faces.append(idx)
    return np.asarray(verts), faces

def area_centroid(verts, faces):
    tot_a = 0.0
    tot_c = np.zeros(3)
    for f in faces:
        a = verts[f[0]]
        b = verts[f[1]]
        c = verts[f[2]]
        n = np.cross(b - a, c - a)
        ar = 0.5 * float(np.linalg.norm(n))
        tot_a += ar
        tot_c += ar * (a + b + c) / 3.0
    return tot_c / tot_a, tot_a

def pcd_centroid(path):
    pts = []
    with open(path) as f:
        in_data = False
        for line in f:
            if not in_data:
                if line.startswith('DATA'):
                    in_data = True
                continue
            p = line.split()
            pts.append([float(p[0]), float(p[1]), float(p[2])])
    arr = np.asarray(pts)
    return arr.mean(axis=0), arr.std(axis=0), len(arr)

mesh_dir = '/data/gpfs/projects/punim2657/Dataset/Mesh/Juglet'
stage = '/data/gpfs/projects/punim2657/SfSpp/runs/20261031-0352_4a4b39b_t47-jugletcc/out/staging'
for n in (1, 3, 5, 9):
    name = 'Juglet_Piece_' + str(n)
    v, faces = obj_mesh(mesh_dir + '/' + name + '_Mesh.obj')
    ac, area = area_centroid(v, faces)
    vc = v.mean(axis=0)
    pc, ps, cnt = pcd_centroid(stage + '/' + name + '_Point.pcd')
    d_vertex = float(np.linalg.norm(pc - vc))
    d_area = float(np.linalg.norm(pc - ac))
    print(name, 'npts=' + str(cnt), 'vertex_delta_mm=' + ('%.3f' % d_vertex), 'area_delta_mm=' + ('%.3f' % d_area))
