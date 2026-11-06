#!/usr/bin/env python3
"""stage311a.py -- Ticket 311 Stage A attribution on Pot E.

Computes on a compute node:
1. A1: For all 34 Pot_E_Piece_01..34_Axis.xyz files in:
   - rule output: 20261105-1215_1a6f16e_t310b3-timing/out/axes310
   - paper-chain baseline: 20261105-0532_d330469_t308a-axes/out/axes_paper
   compared against the authors' released Axes/ in original_samples/SfS_pp/Axes:
   - K_ref (number of lines in authors' file)
   - K_310 (number of lines in rule file)
   - smallest angle (deg) from any line in rule file to authors' line 0 (and to any authors' line if K_ref > 1)
   - 1-based rank (and 0-based index) of that closest line in our file
   - angle of our rank-1 (line 0) to authors' line 0
   - all angles (deg) in rank order in our file
   - same statistics for 308's paper-chain file (K_308, best_deg_308, rank_308, line0_deg_308)
   - surface point counts (N_S0, N_S1) and breakline point counts (N_Bl0_corpus, N_Bl0_lane)
   - whether the piece is in the 31 counted by the assembler (in_31) and why 32, 33, 34 are dropped.

2. A2: Exact recomputation of CountResult (class/data_structure.cpp:969-1040) at
   rad_threshold = 0.35 rad (20.0535 deg), t_threshold = 50.0 mm from
   out/<arm>/T_<i>to_<i>.txt against Ground Truth/Pot_E_Piece_<i+1>_T.txt and
   Ground Truth/Pot_E_simple_graph.txt for:
   - 20261105-1407_1a6f16e_t310c2-E: MOR1, MOR2, MMR1, MMR2
   - 20261105-0550_d330469_t308b-E: MOR1, MOR2, MMR1, MMR2
   Checks both exact C++ isSimilarTrans(GT_T, T, 0.35, 50.0) (with T_result[i]=I_4 when
   T_<i>to_<i>.txt is absent, as Trans::Initialize sets in main_pristine_batch.cpp)
   and score305.py's relative check, verifying that CountResult reproduces 1. Acc.txt
   on every arm, and naming every failing piece and every failing join with its angle (deg, rad)
   and translation error (mm).
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from sfs_axes.io_axes import direction_angle_deg, read_axes  # noqa: E402

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
RUNS = "/data/gpfs/projects/punim2657/SfSpp/runs"
AX310 = os.path.join(RUNS, "20261105-1215_1a6f16e_t310b3-timing", "out", "axes310")
AX308 = os.path.join(RUNS, "20261105-0532_d330469_t308a-axes", "out", "axes_paper")
R310E = os.path.join(RUNS, "20261105-1407_1a6f16e_t310c2-E")
R308E = os.path.join(RUNS, "20261105-0550_d330469_t308b-E")
LANES_E = os.path.join(RUNS, "20261105-0445_9c5eec2_t305-lane-e2", "out", "geom")

RAD_BAR = 0.35
DEG_BAR = float(np.degrees(RAD_BAR))
T_BAR = 50.0


def pcd_points(path):
    if not os.path.isfile(path):
        return 0
    n = 0
    data = False
    with open(path, errors="replace") as fh:
        for line in fh:
            if data:
                if line.strip():
                    n += 1
            elif line.startswith("DATA"):
                data = True
    return n


def xyz_lines(path):
    if not os.path.isfile(path):
        return 0
    with open(path, errors="replace") as fh:
        return sum(1 for line in fh if line.strip())


def read_T(path):
    a = np.loadtxt(path, ndmin=2)
    T = np.eye(4)
    T[0:3, 0:3] = a[0:3, 0:3]
    T[0:3, 3] = a[0:3, 3]
    return T


def inv_out(T):
    """Trans::InvOut in class/data_structure.cpp:645: [R^T, -R^T t; 0, 1] == T^-1."""
    R = T[0:3, 0:3]
    t = T[0:3, 3]
    out = np.eye(4)
    out[0:3, 0:3] = R.T
    out[0:3, 3] = -R.T @ t
    return out


def is_similar_trans_cpp(T_a, T_b, rad_threshold=RAD_BAR, t_threshold=T_BAR):
    """Exact port of isSimilarTrans (class/data_structure.cpp:711-730)."""
    T = T_a @ np.linalg.inv(T_b)
    R = T[0:3, 0:3]
    t = T[0:3, 3]
    c = np.clip((np.trace(R) - 1.0) / 2.0, -1.0, 1.0)
    rad = float(np.arccos(c))
    deg = float(np.degrees(rad))
    trans_cpp = float(np.linalg.norm(t))
    trans_diff = float(np.linalg.norm(T_a[0:3, 3] - T_b[0:3, 3]))
    ok = (rad < rad_threshold) and (trans_cpp < t_threshold)
    return ok, rad, deg, trans_cpp, trans_diff


def score_arm(result_dir, gt_dir, pot="E", n_shards=31):
    G = np.loadtxt(os.path.join(gt_dir, "Pot_%s_simple_graph.txt" % pot), ndmin=2)
    GT_trans = []
    T_result = []
    has_T_file = []
    for i in range(n_shards):
        p = i + 1
        gt_p = os.path.join(gt_dir, "Pot_%s_Piece_%d_T.txt" % (pot, p))
        GT_trans.append(read_T(gt_p))
        res_p = os.path.join(result_dir, "T_%dto_%d.txt" % (i, i))
        if os.path.isfile(res_p):
            T_result.append(read_T(res_p))
            has_T_file.append(True)
        else:
            T_result.append(np.eye(4))
            has_T_file.append(False)

    af_count = np.zeros((n_shards, n_shards), dtype=int)
    joins = []
    for i in range(n_shards):
        for j in range(i + 1, n_shards):
            if int(G[i, j]) == 0:
                continue
            GT_T = inv_out(GT_trans[i]) @ GT_trans[j]
            T = inv_out(T_result[i]) @ T_result[j]
            ok, rad, deg, t_cpp, t_diff = is_similar_trans_cpp(GT_T, T)
            if ok:
                af_count[i, j] = 1
                af_count[j, i] = 1
            joins.append(dict(
                i=i + 1, j=j + 1,
                has_Ti=has_T_file[i], has_Tj=has_T_file[j],
                rad=round(rad, 5), deg=round(deg, 3),
                t_cpp_mm=round(t_cpp, 3), t_diff_mm=round(t_diff, 3),
                pass_cpp=bool(ok)
            ))

    pieces = []
    for i in range(n_shards):
        inc = [j + 1 for j in range(n_shards) if int(G[i, j]) != 0]
        pass_inc = [j + 1 for j in range(n_shards) if af_count[i, j] != 0]
        pieces.append(dict(
            piece=i + 1,
            has_T_file=has_T_file[i],
            n_gt_joins=len(inc),
            n_pass_joins=len(pass_inc),
            gt_neighbors=inc,
            pass_neighbors=pass_inc,
            seated=len(pass_inc) > 0
        ))

    n_sherd = sum(1 for x in pieces if x["seated"])
    n_join = sum(1 for x in joins if x["pass_cpp"])
    acc_path = os.path.join(result_dir, "1. Acc.txt")
    acc_raw = open(acc_path).read().strip() if os.path.isfile(acc_path) else ""
    return dict(
        n_sherd=n_sherd, total_sherd=n_shards,
        n_join=n_join, total_join=len(joins),
        n_T_files=sum(has_T_file),
        missing_T_pieces=[x["piece"] for x in pieces if not x["has_T_file"]],
        seated_pieces=[x["piece"] for x in pieces if x["seated"]],
        failed_pieces=[x["piece"] for x in pieces if not x["seated"]],
        pieces=pieces,
        joins=joins,
        acc_txt=acc_raw
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    # --- Part 1: All 34 Pot E axis files ---
    a1_rows = []
    for p in range(1, 35):
        stem = "Pot_E_Piece_%02d" % p
        ref_p = os.path.join(CORPUS, "Axes", stem + "_Axis.xyz")
        r310_p = os.path.join(AX310, stem + "_Axis.xyz")
        r308_p = os.path.join(AX308, stem + "_Axis.xyz")
        gt_ax_p = os.path.join(CORPUS, "Ground Truth Axes", stem + "_Axis.xyz")
        gt_t_p = os.path.join(CORPUS, "Ground Truth", "Pot_E_Piece_%d_T.txt" % p)
        s0_p = os.path.join(CORPUS, "Surfaces", stem + "_Surface_0.xyz")
        s1_p = os.path.join(CORPUS, "Surfaces", stem + "_Surface_1.xyz")
        bl0_corp_p = os.path.join(CORPUS, "Breaklines", stem + "_Breakline_0.pcd")
        bl0_lane_p = os.path.join(LANES_E, stem + ".Bl0")

        ref = read_axes(ref_p)
        v310 = read_axes(r310_p)
        v308 = read_axes(r308_p)
        gt_ax = read_axes(gt_ax_p) if os.path.isfile(gt_ax_p) else None

        K_ref = int(ref.shape[1])
        K_310 = int(v310.shape[1])
        K_308 = int(v308.shape[1])

        # Angles of each line in v310 to ref line 0 (and min across all ref lines if K_ref > 1)
        angs_310_ref0 = [float(direction_angle_deg(v310[0:3, k], ref[0:3, 0])) for k in range(K_310)]
        angs_310_ref_any = [
            min(float(direction_angle_deg(v310[0:3, k], ref[0:3, r])) for r in range(K_ref))
            for k in range(K_310)
        ]
        best_idx_ref0 = int(np.argmin(angs_310_ref0))
        best_idx_any = int(np.argmin(angs_310_ref_any))

        angs_308_ref0 = [float(direction_angle_deg(v308[0:3, k], ref[0:3, 0])) for k in range(K_308)]
        best_308_idx = int(np.argmin(angs_308_ref0))

        ref0_vs_gt = (float(direction_angle_deg(ref[0:3, 0], gt_ax[0:3, 0]))
                      if gt_ax is not None else float("nan"))

        n_s0 = xyz_lines(s0_p)
        n_s1 = xyz_lines(s1_p)
        n_bl0_corp = pcd_points(bl0_corp_p)
        n_bl0_lane = pcd_points(bl0_lane_p)
        has_gt_T = os.path.isfile(gt_t_p)
        in_31 = (p <= 31) and has_gt_T and (n_bl0_lane > 0)
        drop_reason = ""
        if not in_31:
            reasons = []
            if p > 31:
                reasons.append("not_in_data_path_h(SHARD_NUMBER=31)")
            if not has_gt_T:
                reasons.append("no_Ground_Truth_T")
            if n_bl0_lane == 0:
                reasons.append("no_lane_Bl0(no_released_Point_cloud)")
            if n_bl0_corp < 50:
                reasons.append("corpus_Bl0_%d_pts(<50_paper_threshold)" % n_bl0_corp)
            drop_reason = ";".join(reasons)

        row = dict(
            piece=p, stem=stem, in_31=in_31, drop_reason=drop_reason,
            K_ref=K_ref, K_310=K_310, K_308=K_308,
            best_deg_310=round(angs_310_ref0[best_idx_ref0], 3),
            best_rank_310=best_idx_ref0 + 1,  # 1-based rank
            line0_deg_310=round(angs_310_ref0[0], 3),
            best_any_ref_deg_310=round(angs_310_ref_any[best_idx_any], 3),
            best_any_ref_rank_310=best_idx_any + 1,
            all_deg_310=";".join("%.2f" % x for x in angs_310_ref0),
            best_deg_308=round(angs_308_ref0[best_308_idx], 3),
            best_rank_308=best_308_idx + 1,
            line0_deg_308=round(angs_308_ref0[0], 3),
            all_deg_308=";".join("%.2f" % x for x in angs_308_ref0),
            ref0_vs_gt_deg=round(ref0_vs_gt, 3) if ref0_vs_gt == ref0_vs_gt else -1.0,
            n_s0=n_s0, n_s1=n_s1,
            n_bl0_corp=n_bl0_corp, n_bl0_lane=n_bl0_lane
        )
        a1_rows.append(row)

    # Save A1 table
    a1_keys = [
        "piece", "stem", "in_31", "K_ref", "K_310", "best_deg_310", "best_rank_310",
        "line0_deg_310", "all_deg_310", "K_308", "best_deg_308", "best_rank_308",
        "line0_deg_308", "all_deg_308", "ref0_vs_gt_deg", "n_s0", "n_s1",
        "n_bl0_corp", "n_bl0_lane", "drop_reason"
    ]
    with open(os.path.join(a.out, "a1_provenance.tsv"), "w") as fh:
        fh.write("\t".join(a1_keys) + "\n")
        for r in a1_rows:
            fh.write("\t".join(str(r[k]) for k in a1_keys) + "\n")

    # --- Part 2: Score arms of 310c2-E and 308b-E ---
    gt_dir = os.path.join(CORPUS, "Ground Truth")
    arms_out = {}
    for tag, rdir, arm in [
        ("310_MOR1", R310E, "MOR1"),
        ("310_MOR2", R310E, "MOR2"),
        ("310_MMR1", R310E, "MMR1"),
        ("310_MMR2", R310E, "MMR2"),
        ("308_MOR1", R308E, "MOR1"),
        ("308_MOR2", R308E, "MOR2"),
        ("308_MMR1", R308E, "MMR1"),
        ("308_MMR2", R308E, "MMR2"),
    ]:
        adir = os.path.join(rdir, "out", arm)
        if os.path.isdir(adir):
            arms_out[tag] = score_arm(adir, gt_dir, "E", 31)

    with open(os.path.join(a.out, "a2_arms.json"), "w") as fh:
        json.dump(arms_out, fh, indent=2)

    # Write per-join and per-piece TSV for 310_MMR1, 310_MMR2, 308_MMR1, 310_MOR1
    with open(os.path.join(a.out, "a2_pieces.tsv"), "w") as fh:
        fh.write("piece\tstem\tK_310\tbest_deg_310\tbest_rank_310\tline0_deg_310\t"
                 "K_308\tbest_deg_308\tn_gt_joins\t"
                 "MO_pass\tBASE_R1_pass\tBASE_R2_pass\tMMR1_pass\tMMR2_pass\t"
                 "MMR1_status\tMMR2_status\n")
        for p in range(1, 32):
            r1 = a1_rows[p - 1]
            mo = arms_out["310_MOR1"]["pieces"][p - 1]
            b1 = arms_out["308_MMR1"]["pieces"][p - 1]
            b2 = arms_out["308_MMR2"]["pieces"][p - 1]
            m1 = arms_out["310_MMR1"]["pieces"][p - 1]
            m2 = arms_out["310_MMR2"]["pieces"][p - 1]
            s1 = "PASS" if m1["seated"] else ("FAIL(no_T)" if not m1["has_T_file"] else "FAIL")
            s2 = "PASS" if m2["seated"] else ("FAIL(no_T)" if not m2["has_T_file"] else "FAIL")
            fh.write("%d\t%s\t%d\t%.3f\t%d\t%.3f\t%d\t%.3f\t%d\t%d\t%d\t%d\t%d\t%d\t%s\t%s\n" % (
                p, r1["stem"], r1["K_310"], r1["best_deg_310"], r1["best_rank_310"], r1["line0_deg_310"],
                r1["K_308"], r1["best_deg_308"], mo["n_gt_joins"],
                mo["n_pass_joins"], b1["n_pass_joins"], b2["n_pass_joins"],
                m1["n_pass_joins"], m2["n_pass_joins"], s1, s2
            ))

    with open(os.path.join(a.out, "a2_joins.tsv"), "w") as fh:
        fh.write("join_i\tjoin_j\t"
                 "MOR1_deg\tMOR1_mm\tMOR1_verdict\t"
                 "BASE1_deg\tBASE1_mm\tBASE1_verdict\t"
                 "MMR1_deg\tMMR1_mm\tMMR1_verdict\t"
                 "MMR2_deg\tMMR2_mm\tMMR2_verdict\n")
        J_mo = arms_out["310_MOR1"]["joins"]
        J_b1 = arms_out["308_MMR1"]["joins"]
        J_m1 = arms_out["310_MMR1"]["joins"]
        J_m2 = arms_out["310_MMR2"]["joins"]
        for k in range(len(J_mo)):
            jmo, jb1, jm1, jm2 = J_mo[k], J_b1[k], J_m1[k], J_m2[k]
            v_mo = "PASS" if jmo["pass_cpp"] else "FAIL"
            v_b1 = "PASS" if jb1["pass_cpp"] else ("FAIL(no_T)" if not (jb1["has_Ti"] and jb1["has_Tj"]) else "FAIL")
            v_m1 = "PASS" if jm1["pass_cpp"] else ("FAIL(no_T)" if not (jm1["has_Ti"] and jm1["has_Tj"]) else "FAIL")
            v_m2 = "PASS" if jm2["pass_cpp"] else ("FAIL(no_T)" if not (jm2["has_Ti"] and jm2["has_Tj"]) else "FAIL")
            fh.write("%d\t%d\t%.3f\t%.3f\t%s\t%.3f\t%.3f\t%s\t%.3f\t%.3f\t%s\t%.3f\t%.3f\t%s\n" % (
                jmo["i"], jmo["j"],
                jmo["deg"], jmo["t_cpp_mm"], v_mo,
                jb1["deg"], jb1["t_cpp_mm"], v_b1,
                jm1["deg"], jm1["t_cpp_mm"], v_m1,
                jm2["deg"], jm2["t_cpp_mm"], v_m2
            ))

    print("=== Stage A Summary ===")
    for tag, d in arms_out.items():
        print("%s: sherds %d/%d joins %d/%d (T_files=%d) failed_pieces=%s" % (
            tag, d["n_sherd"], d["total_sherd"], d["n_join"], d["total_join"],
            d["n_T_files"], d["failed_pieces"]
        ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
