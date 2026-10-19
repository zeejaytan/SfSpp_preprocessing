# 175 probe1: edge-dot disposition + class seating + local radius structure. Ruler for scoring only.
import numpy as np
H = "C:/PR/SfSpp_preprocessing/.scratch/pota175_repro"
log = open(H + "/p175_probe1.txt", "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
d = np.load("C:/PR/SfSpp_preprocessing/.scratch/pota173_repro/p173_bag.npz", allow_pickle=True)
BAG, G0 = d["BAG"], d["G0"]
z = np.load(H + "/p175_probe0.npz")
alB, rB, ang, dr, sta, dmin = z["alB"], z["rB"], z["ang"], z["dr"], z["sta"], z["dmin"]
inner = dr <= 1.0; outer = dr > 2.5; mid = (~inner)&(~outer)
pred_in = alB < -0.5; pred_out = alB > 0.5; pred_edge = ~(pred_in|pred_out)
say("pred split: inner-face=%d outer-face=%d edge=%d (total %d)" % (int(pred_in.sum()), int(pred_out.sum()), int(pred_edge.sum()), len(BAG)))
for nm, m in [("pred-inner",pred_in),("pred-outer",pred_out),("pred-edge",pred_edge)]:
    say("%s: ruler inner=%d outer=%d mid=%d | dmin<2: %d (%.1f%%) | dmin med=%.2f" % (
        nm, int((m&inner).sum()), int((m&outer).sum()), int((m&mid).sum()),
        int((dmin[m]<2).sum()), float((dmin[m]<2).mean()*100), float(np.median(dmin[m]))))
# confusion: ruler-outer dots landing pred-inner and vice versa
say("ruler-outer in pred-inner: %d/130; ruler-inner in pred-outer: %d/450" % (int((outer&pred_in).sum()), int((inner&pred_out).sum())))
# edge dots: ruler + seating
e = pred_edge
say("edge: sta coverage %d/211 stations; dmin<2 stations %d/211" % (
    len(set(sta[e].tolist())), len(set(sta[e&(dmin<2)].tolist()))))
# per-angular-bin: edge radius vs face radii (local split test)
nb=72
bins=(np.floor((ang+np.pi)/(2*np.pi)*nb)).astype(int).clip(0,nb-1)
loc_ok = 0; loc_tot = 0; edge_near_in = 0; edge_near_out = 0
for b in range(nb):
    m = bins==b
    if e[m].sum()==0: continue
    ri = rB[m&pred_in]; ro = rB[m&pred_out]; re = rB[m&e]
    if len(ri)==0 or len(ro)==0: continue
    loc_tot += 1
    thi = np.median(ri); tho = np.median(ro)
    if thi < tho: loc_ok += 1
    for x in re:
        if abs(x-thi) <= abs(x-tho): edge_near_in += 1
        else: edge_near_out += 1
say("bins with inner+outer present: %d; inner-med<outer-med: %d" % (loc_tot, loc_ok))
say("edge dots nearer local inner-med vs outer-med: %d vs %d" % (edge_near_in, edge_near_out))
# global-radius edge split alternative
say("edge radius med=%.2f vs inner med=%.2f outer med=%.2f" % (float(np.median(rB[e])), float(np.median(rB[pred_in])), float(np.median(rB[pred_out]))))
# station coverage per class
for nm, m in [("pred-inner",pred_in),("pred-outer",pred_out),("pred-edge",pred_edge)]:
    cov = len(set(sta[m&(dmin<2)].tolist()))
    say("%s station cover (dmin<2): %d/211" % (nm, cov))
log.close(); print("probe1 done")
