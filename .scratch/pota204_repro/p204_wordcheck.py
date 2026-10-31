import sys; sys.path.insert(0, ".scratch/pota201_repro")
import numpy as np, json, os
from p201_lib import compute_features, quantize, longest_run, arc_stats, read_pcd

H204 = ".scratch/pota204_repro"
G0 = {"01": ".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_0.pcd",
      "02": H204+"/ORIG_C02_Bl0.pcd", "03": H204+"/ORIG_C03_Bl0.pcd", "04": H204+"/ORIG_C04_Bl0.pcd"}
FR = {"01": H204+"/FRESH_C01_Bl0.pcd", "02": H204+"/FRESH_C02_Bl0.pcd",
      "03": H204+"/FRESH_C03_Bl0.pcd", "04": H204+"/FRESH_C04_Bl0.pcd"}
log = open(os.path.join(H204, "p204_wordcheck.txt"), "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
out = {}
def words(X, A, tag):
    f6x = compute_features(X); f6a = compute_features(A)
    qx = quantize(np.vstack([f6x, np.zeros(f6x.shape[1])]))
    qa = quantize(np.vstack([f6a, np.zeros(f6a.shape[1])]))
    bf, ef = longest_run(qx, qa); br, er = longest_run(qx, qa[:, ::-1])
    n, m = int(qx.shape[1]), int(qa.shape[1])
    st = arc_stats(X)
    dsteps = np.linalg.norm(np.diff(np.vstack([X, X[:1]]), axis=0), axis=1)
    toks = np.unique(np.floor(dsteps / 0.15).astype(int))
    say("  %s: n=%d m=%d fwdLCS=%d (cov %.3f) revLCS=%d (cov %.3f) arc=%.1f closure=%.2f dTok=%d" % (
        tag, n, m, int(bf), float(bf)/min(n,m), int(br), float(br)/min(n,m), float(st['arc']), float(st['closure']), int(len(toks))))
    return dict(n=n, m=m, fwd=int(bf), fwd_cov=round(float(bf)/min(n,m),3), rev=int(br),
                rev_cov=round(float(br)/min(n,m),3), arc=round(float(st['arc']),1),
                closure=round(float(st['closure']),2), dtok=int(len(toks)))
for pc in ["01","02","03","04"]:
    say("="*70); say("PIECE C"+pc); d = out[pc] = {}
    TH = np.load(os.path.join(H204, "p204_C%s_true_seated.npy" % pc))
    Fresh, _, _ = read_pcd(FR[pc]); Auth, _, _ = read_pcd(G0[pc])
    d['thin_vs_auth'] = words(TH, Auth, "thin-vs-Bl0")
    d['fresh_vs_auth'] = words(Fresh, Auth, "fresh-vs-Bl0")
say("="*70)
say("C01 calibrator (201): seating needed fwd ~0.5 (C01 thin 0.544 seats)")
json.dump(out, open(os.path.join(H204, "p204_words.json"), "w"), indent=1, default=int)
say("P204 WORDCHECK DONE"); log.close(); print("P204 WORDCHECK DONE")
