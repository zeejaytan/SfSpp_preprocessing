"""POTA-214: mesh-area census for Point-PCD sampling density calibration.
Reads ORIG Pot_D Mesh_DS OBJs (+ Pot_A legacy reference) on Spartan, prints
vertex/face counts and triangle area per piece. Pure stdlib."""
import sys, math

def mesh_area(path):
    verts = []
    nv = nf = 0
    area = 0.0
    with open(path) as f:
        for line in f:
            if line.startswith('v '):
                p = line.split()
                verts.append((float(p[1]), float(p[2]), float(p[3])))
                nv += 1
            elif line.startswith('f '):
                p = line.split()[1:]
                idx = [int(x.split('/')[0]) - 1 for x in p]
                nf += 1
                # fan triangulation
                a = verts[idx[0]]
                for k in range(1, len(idx) - 1):
                    b = verts[idx[k]]
                    c = verts[idx[k + 1]]
                    ab = (b[0]-a[0], b[1]-a[1], b[2]-a[2])
                    ac = (c[0]-a[0], c[1]-a[1], c[2]-a[2])
                    cr = (ab[1]*ac[2]-ab[2]*ac[1], ab[2]*ac[0]-ab[0]*ac[2], ab[0]*ac[1]-ab[1]*ac[0])
                    area += 0.5 * math.sqrt(cr[0]**2 + cr[1]**2 + cr[2]**2)
    return nv, nf, area

base = sys.argv[1] if len(sys.argv) > 1 else '.'
pieces = sys.argv[2].split(',') if len(sys.argv) > 2 else []
for pc in pieces:
    nv, nf, area = mesh_area('%s/%s' % (base, pc))
    print('%s verts=%d faces=%d area=%.1fmm2' % (pc, nv, nf, area))
