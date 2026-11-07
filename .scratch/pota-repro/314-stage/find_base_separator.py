import glob, os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.io_axes import read_axes

# Ground truth base pieces: pieces where released axis has d < 25mm
pieces_info = []
for pdir in sorted(glob.glob(f"{CORPUS}/Axes/*_Axis.xyz")):
    stem = os.path.basename(pdir).replace("_Axis.xyz", "")
    s0_p = f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz"
    s1_p = f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz"
    if not os.path.exists(s0_p): continue
    s0 = np.loadtxt(s0_p, usecols=range(6)).T
    s1 = np.loadtxt(s1_p, usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    
    axes = read_axes(pdir)
    c_pt = C[:3].mean(axis=1)
    min_d = 999.0
    for k in range(axes.shape[1]):
        a = axes[:3, k] / np.linalg.norm(axes[:3, k])
        p0 = axes[3:6, k]
        d = np.linalg.norm(np.cross(c_pt - p0, a))
        if d < min_d: min_d = d
    is_base = (min_d < 25.0)

    # Let us compute several geometric invariants of C:
    # 1. Surface normal PCA:
    # On a wall piece (cylinder), normals form an arc in 2D, so eigenvalues are [lambda1, lambda2, lambda3]
    # where lambda3 is small (cylinder axis).
    # On a base floor disk, normals all point in one direction, so lambda2 and lambda3 are BOTH small!
    cov_N = np.cov(C[3:6, :])
    e_N = np.sort(np.linalg.eigvalsh(cov_N))[::-1] # descending
    # ratio lambda2 / lambda1: for cylinder, normals fan out in a circle, so lambda1 ~ lambda2?
    # No, for a planar patch, normals don't fan out at all!
    
    # 2. What about the distribution of normal distances?
    # In Pottmann space, line coordinates of normals:
    # (n, p x n).
    # What is the Pottmann cost of the best cylinder vs best plane?
    # 3. What is the radius of the piece in 3D?
    P = C[:3, :] - c_pt[:, None]
    cov_P = np.cov(P)
    e_P = np.sort(np.linalg.eigvalsh(cov_P))[::-1]
    
    # 4. What about candidate axes with d < 25mm:
    # When a candidate axis vt has d < 25mm:
    # Look at the radius r of points from vt:
    # For a perpendicular decoy, as r increases, what happens to the normals?
    # For a perpendicular decoy, as r increases, the distance along the wall increases.
    # But wait! On a vessel of revolution (true base):
    # A true base piece containing the axis has the rotation axis AT ITS CENTER!
    # Points exist at r in [0, R_base].
    # In a perpendicular wall piercing, the axis pierces the wall.
    # What is the distance between the two surfaces along the axis?
    # The axis enters Surface 0 and exits Surface 1 (or vice versa).
    # The distance between the entrance point and exit point is THE WALL THICKNESS (~ 5 to 10 mm)!
    # Whereas for a true base rotation axis, the axis does NOT pierce through the ceramic wall!
    # The axis is in EMPTY SPACE (or passes through the base floor center)!
    
    pieces_info.append((stem, is_base, min_d, e_N, e_P))

print(f"Total pieces: {len(pieces_info)}")
print(f"Base pieces (min_d < 25mm): {sum(1 for x in pieces_info if x[1])}")
for stem, is_base, min_d, e_N, e_P in pieces_info:
    if is_base or "Pot_E" in stem:
        status = "BASE" if is_base else "WALL"
        print(f"{stem:18s} [{status:4s}] min_d={min_d:5.1f} | e_N={np.round(e_N, 3)} | e_P={np.round(e_P, 1)}")
