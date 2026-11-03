#!/usr/bin/env python3
"""pairs68.py OUT_DIR ARM [ARM...] -- per-GT-pair table from the t67 attitude instrument.

Reads <OUT_DIR>/<ARM>/T67_{gtpairs,candidates,survivors}.tsv. For each GT pair: number of LCS
candidates, the best candidate by rotation error (dots matched = size, inliers, ICP score, folded
axis angle, rotation error, centroid error), and where the pair dies. Death order follows
PairwisePruning (feature_matching.cpp:1715 axis gate > 25 deg, :1726 score gate > 1.5, :1729 overlap)
as read in t67: a candidate survives only if it is in T67_survivors.tsv.
Focus rows: the 10 GT joins touching 2/5/9 and the joins among {1,5,7,8}.
"""
import csv
import os
import sys


def rows(p):
    if not os.path.exists(p):
        return []
    with open(p) as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def death(c, surv):
    if (c["fix"], c["mov"], c["idx"]) in surv:
        return "SURVIVES"
    if float(c["score"]) > 1.5:
        return "score gate"
    if float(c["axis_fold_deg"]) > 25.0:
        return "axis gate"
    return "overlap/other"


def main():
    od, arms = sys.argv[1], sys.argv[2:]
    for arm in arms:
        d = os.path.join(od, arm)
        gtp = rows(os.path.join(d, "T67_gtpairs.tsv"))
        cand = rows(os.path.join(d, "T67_candidates.tsv"))
        surv = {(s["fix"], s["mov"], s["idx"]) for s in rows(os.path.join(d, "T67_survivors.tsv"))}
        print("=== %s: %d candidates, %d GT-edge candidates, %d survivors %s" % (
            arm, len(cand), sum(c["gt_edge"] == "1" for c in cand), len(surv),
            sorted((s[0], s[1]) for s in surv)))
        gtc = [c for c in cand if c["gt_edge"] == "1"]
        if gtc:
            sz = sorted(int(c["size"]) for c in gtc)
            print("GT-edge matched-run length (dots): min %d median %d max %d mean %.1f" % (
                sz[0], sz[len(sz) // 2], sz[-1], sum(sz) / len(sz)))
        print("pair\tfocus\tgt_axis_fold\tdots_f/m\tcontacts\tn_cand\tbest: size inl score fold rot cen\tdies")
        for g in gtp:
            f, m = g["fix"], g["mov"]
            fs = {f, m}
            focus = "259" if fs & {"2", "5", "9"} else ("placed" if fs <= {"1", "5", "7", "8"} else "")
            un = float(g["gt_axis_unfold_deg"])
            fold = min(un, 180 - un)
            cs = [c for c in cand if {c["fix"], c["mov"]} == fs]
            if cs:
                b = min(cs, key=lambda c: float(c["rot_err_deg"]))
                best = "%s %s %.2f %.1f %.1f %.1f" % (b["size"], b["inlier"], float(b["score"]),
                                                      float(b["axis_fold_deg"]), float(b["rot_err_deg"]),
                                                      float(b["centroid_err_mm"]))
                ds = sorted({death(c, surv) for c in cs})
                dies = ",".join(ds)
            else:
                best, dies = "-", "no LCS"
            print("%s-%s\t%s\t%.1f\t%s/%s\t%s\t%d\t%s\t%s" % (f, m, focus, fold, g["dots_fix"], g["dots_mov"],
                                                         g["gt_contact_lt2mm"], len(cs), best, dies))


if __name__ == "__main__":
    main()
