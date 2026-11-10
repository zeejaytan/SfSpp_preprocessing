import math, os
base = r"C:/PR/worktrees/sfs/325/artifacts/pota325/axes"

def lines(d, i):
    p = os.path.join(d, f"Juglet_Piece_{i}_Axis.xyz")
    return [l.split() for l in open(p) if l.strip()]

def ang(u, v):
    du = sum(a*b for a, b in zip(u, v)) / (math.dist([0]*3, u) * math.dist([0]*3, v))
    return math.degrees(math.acos(max(-1, min(1, du))))

print("piece  n_a325 n_t323 | a325 rank0 best3 | t323 rank0 best3")
r0_325, b3_325, r0_323, b3_323 = [], [], [], []
for i in range(1, 10):
    g = lines(os.path.join(base, "gt"), i)
    gd = [float(x) for x in g[0][3:6]]
    row = []
    for tag in ("a325", "t323"):
        ls = lines(os.path.join(base, tag), i)
        errs = [ang([float(x) for x in l[3:6]], gd) for l in ls]
        row.append((len(ls), errs[0], min(errs)))
    r0_325.append(row[0][1]); b3_325.append(row[0][2])
    r0_323.append(row[1][1]); b3_323.append(row[1][2])
    print(f"{i:5d} {row[0][0]:6d} {row[1][0]:6d} | {row[0][1]:10.2f} {row[0][2]:10.2f} | {row[1][1]:10.2f} {row[1][2]:10.2f}")
for name, v in (("axes325 rank0", r0_325), ("axes325 best3", b3_325), ("axes323 rank0", r0_323), ("axes323 best3", b3_323)):
    print(f"{name:14s} <=10deg {sum(1 for x in v if x <= 10)}/9   <=30deg {sum(1 for x in v if x <= 30)}/9   max {max(v):.2f}")
