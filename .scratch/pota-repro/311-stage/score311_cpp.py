#!/usr/bin/env python3
"""score311_cpp.py RESULT_DIR GT_DIR POT OUT_JSON LABEL

Recomputes CountResult (class/data_structure.cpp:969-1040) at rad_threshold=0.35,
t_threshold=50.0 from T_<i>to_<i>.txt against Ground Truth/Pot_<POT>_Piece_<i+1>_T.txt.
"""
import json
import os
import sys

import numpy as np

RAD_BAR = 0.35
T_BAR = 50.0


def read_T(path):
    a = np.loadtxt(path, ndmin=2)
    T = np.eye(4)
    T[0:3, 0:3] = a[0:3, 0:3]
    T[0:3, 3] = a[0:3, 3]
    return T


def inv_out(T):
    R = T[0:3, 0:3]
    t = T[0:3, 3]
    out = np.eye(4)
    out[0:3, 0:3] = R.T
    out[0:3, 3] = -R.T @ t
    return out


def is_similar_trans_cpp(T_a, T_b):
    T = T_a @ np.linalg.inv(T_b)
    R = T[0:3, 0:3]
    t = T[0:3, 3]
    c = np.clip((np.trace(R) - 1.0) / 2.0, -1.0, 1.0)
    rad = float(np.arccos(c))
    deg = float(np.degrees(rad))
    trans_cpp = float(np.linalg.norm(t))
    ok = (rad < RAD_BAR) and (trans_cpp < T_BAR)
    return ok, rad, deg, trans_cpp


def main():
    result_dir, gt_dir, pot, out_json, label = sys.argv[1:6]
    G = np.loadtxt(os.path.join(gt_dir, "Pot_%s_simple_graph.txt" % pot), ndmin=2)
    n_shards = G.shape[0]
    GT_trans, T_result, has_T = [], [], []
    for i in range(n_shards):
        p = i + 1
        GT_trans.append(read_T(os.path.join(gt_dir, "Pot_%s_Piece_%d_T.txt" % (pot, p))))
        rp = os.path.join(result_dir, "T_%dto_%d.txt" % (i, i))
        if os.path.isfile(rp):
            T_result.append(read_T(rp))
            has_T.append(True)
        else:
            T_result.append(np.eye(4))
            has_T.append(False)

    af_count = np.zeros((n_shards, n_shards), dtype=int)
    joins = []
    for i in range(n_shards):
        for j in range(i + 1, n_shards):
            if int(G[i, j]) == 0:
                continue
            GT_T = inv_out(GT_trans[i]) @ GT_trans[j]
            T = inv_out(T_result[i]) @ T_result[j]
            ok, rad, deg, t_cpp = is_similar_trans_cpp(GT_T, T)
            if ok:
                af_count[i, j] = 1
                af_count[j, i] = 1
            joins.append(dict(
                i=i + 1, j=j + 1,
                has_Ti=has_T[i], has_Tj=has_T[j],
                deg=round(deg, 3), t_mm=round(t_cpp, 3),
                pass_cpp=bool(ok)
            ))

    seated = [i + 1 for i in range(n_shards) if af_count[i, :].sum() > 0]
    failed = [i + 1 for i in range(n_shards) if af_count[i, :].sum() == 0]
    missing_T = [i + 1 for i in range(n_shards) if not has_T[i]]
    acc_p = os.path.join(result_dir, "1. Acc.txt")
    acc_txt = open(acc_p).read().strip() if os.path.isfile(acc_p) else ""
    out = dict(
        label=label,
        n_sherd=len(seated), total_sherd=n_shards,
        n_join=sum(1 for x in joins if x["pass_cpp"]), total_join=len(joins),
        n_T_files=sum(has_T),
        missing_T_pieces=missing_T,
        seated_pieces=seated,
        failed_pieces=failed,
        failed_joins=["%d-%d(%.1fdeg/%.1fmm)" % (x["i"], x["j"], x["deg"], x["t_mm"])
                      for x in joins if not x["pass_cpp"]],
        joins=joins,
        acc_txt=acc_txt
    )
    with open(out_json, "w") as fh:
        json.dump(out, fh, indent=2)
    print("CPP_SCORE %s: %d/%d sherds, %d/%d joins, failed_pieces=%s" % (
        label, out["n_sherd"], out["total_sherd"], out["n_join"], out["total_join"], failed
    ))


if __name__ == "__main__":
    main()
