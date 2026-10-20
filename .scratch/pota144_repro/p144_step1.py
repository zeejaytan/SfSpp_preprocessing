"""Ticket 144 step1: reproduce greedy-314 control (reproduce-or-stop). Read-only inputs from pota143."""
import numpy as np, os
H = ".scratch/pota144_repro"; P143 = ".scratch/pota143_repro"; INP = ".scratch/pota115_staging/inputs"
os.makedirs(H, exist_ok=True)
log = open(os.path.join(H, "p144_control.txt"), "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
G = np.load(os.path.join(P143, "p143_G314.npy"))
W = len(G)
say("bag G314: %d" % W)
assert W == 314
X32 = G.astype(np.float32)
keys = np.array([X32[i].tobytes() for i in range(W)])
# verbatim walk_plain from p143_step6 (K34+T13 bar arm)
cvis = {keys[0]: 0}; cseq = [0]; cur = 0
for t in range(1, W):
    d = np.sqrt(((G - G[cur]) ** 2).sum(-1))
    idx = np.argsort(d, kind="stable")[:34]
    if t == 1:
        nxt = int(idx[1]); cseq.append(nxt); cvis[keys[nxt]] = 1; cur = nxt; continue
    unv = [int(j) for j in idx if keys[int(j)] not in cvis]
    if not unv: break
    j = unv[0]; cseq.append(j); cvis[keys[j]] = len(cseq) - 1; cur = j
gn = len(cseq)
say("GREEDY-314: greedy=%d/%d ratio=%.4f final=%d" % (gn, W, gn / W, len(cseq)))
# verbatim gate from p143_step6
def load_pcd3(path):
    P = []; HDR = ("VERSION","FIELDS","SIZE","TYPE","COUNT","WIDTH","HEIGHT","VIEWPOINT","POINTS","DATA")
    for ln in open(path):
        s = ln.strip()
        if not s or s[0]=="#" or s.split()[0] in HDR: continue
        try: P.append([float(x) for x in s.split()[:3]])
        except: continue
    return np.array(P)
Ov = load_pcd3(os.path.join(INP, "Bl0.pcd"))
TF = np.loadtxt(os.path.join(INP, "TF.txt")); TO = np.loadtxt(os.path.join(INP, "TO.txt"))
Og = Ov.dot(TO[:3,:3].T) + TO[:3,3]
seq = np.array(cseq)
L = G[seq]; Gf = L.dot(TF[:3,:3].T) + TF[:3,3]
D = np.sqrt(((Gf[:,None,:]-Og[None,:,:])**2).sum(-1)).min(1)
st = np.sqrt(((L[1:]-L[:-1])**2).sum(-1)); nj = int((st>5).sum())
big = float((st[st>=40].max())) if (st>=40).any() else 0.0
DO = np.sqrt(((Og[:,None,:]-Gf[None,:,:])**2).sum(-1)).min(1)
cov = int((DO<2).sum()); unc = int((DO>5).sum())
ui = sorted(np.where(DO>5)[0].tolist())
spans=[]
if ui:
    a=ui[0]; p=ui[0]
    for q in ui[1:]:
        if q==p+1: p=q
        else: spans.append((a,p)); a=q; p=q
    spans.append((a,p))
say("GREEDY gate: final=%d med=%.4f <2mm=%.1f%% gaps5=%d maxstep=%.1f big40=%.1f ORIGcov %d/211 uncovered=%d spans=%s" % (len(seq), float(np.median(D)), float((D<2).mean()*100), nj, float(st.max()), big, cov, unc, spans))
np.save(os.path.join(H, "p144_seq_greedy314.npy"), seq)
# new-dot visits (admitted vs 282 = slots 282..313)
NEW = list(range(282, 314))
pos = {s: (int(np.where(seq == s)[0][0]) if (seq == s).any() else -1) for s in NEW}
say("admitted-32 visits on-road: %d/32" % sum(1 for v in pos.values() if v != -1))
say("poolA slots 282..291: " + str({s: pos[s] for s in range(282, 292)}))
say("grid  slots 292..313: " + str({s: pos[s] for s in range(292, 314)}))
# reproduce-or-stop check vs 143 marks
ok = (gn == 140 and abs(float(np.median(D)) - 3.9851) < 1e-3 and unc == 91 and spans == [(115, 205)])
say("REPRODUCE-OR-STOP: " + ("GREEN" if ok else "RED -- STOP"))
log.close(); print("step1 done")
