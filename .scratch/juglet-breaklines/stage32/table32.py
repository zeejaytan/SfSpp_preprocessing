#!/usr/bin/env python3
"""Ticket 32 -- assemble the cell JSONs into the two tables and the auxiliary tables.

Nothing is computed here beyond formatting: every number comes out of a cell file whose
md5 is listed in out/cells/index.tsv.  A missing cell writes 'na' and the reason.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import io32

JUG = [("J", "%d" % n, "Juglet_Piece_%d" % n) for n in range(1, 10)]
POT = [("PA_native", "%02d" % n, "Pot_A_Piece_%02d" % n) for n in range(1, 9)]
POT25 = [("PA_025", "%02d" % n, "Pot_A_Piece_%02d" % n) for n in range(1, 9)]
ARMS = JUG + POT + POT25
DCELLS = ([("J", "%d" % n) for n in range(1, 10)] + [("PA_025", "07")] +
          [("B", "%d" % n) for n in (2, 3, 5, 7)] +
          [("E", "%d" % n) for n in (2, 3, 5, 7)] + [("PA", "Pot_A_Piece_07")])
WINDOWS = ("1.0", "2.0", "3.0", "5.0")


def load(outdir, name):
    p = os.path.join(outdir, "cells", name + ".json")
    if not os.path.isfile(p):
        return None, "cell %s.json missing (see logs/cells.log)" % name
    with open(p) as f:
        return json.load(f), None


def num(v, fmt="%.6f"):
    if v is None:
        return "na"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        return fmt % v
    return str(v)


def w(path, header, rows):
    with open(path, "w") as f:
        f.write("\t".join(header) + "\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")
    print("[T32] wrote %s (%d rows)" % (path, len(rows)))


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    a = ap.parse_args(argv)
    out = a.outdir
    vessel = {}
    for pot in ("Juglet", "PotA"):
        rec, why = load(out, "A_VESSEL_%s" % pot)
        if rec is None:
            print("[T32] WARNING vessel cell missing: %s" % why)
        else:
            vessel[pot] = rec
    sizes, derive, rows_note = [], [], []
    for arm, key, piece in ARMS:
        rec, why = load(out, "A_%s_%s" % (arm, key))
        pot = "Juglet" if arm == "J" else "PotA"
        vs = vessel.get(pot, {}).get("vessel_mm")
        if rec is None:
            sizes.append([piece, arm, "na", "na", "na", num(vs), "na", why])
            continue
        ext = rec.get("extent_mm")
        ratio = None if (ext is None or vs in (None, 0)) else ext / float(vs)
        note = "%s; %s" % (rec.get("pcd_data"), rec.get("pcd"))
        if rec.get("n_points_subsampled"):
            note += "; voxel %.2f mm, one point per cell, first in file order" % (
                rec["subsample_cell_mm"])
        if rec.get("header_points", -1) != rec.get("n_points"):
            note += "; header POINTS=%s, body=%s" % (rec.get("header_points"),
                                                     rec.get("n_points"))
        sizes.append([piece, arm, rec.get("n_points"), num(ext), num(rec.get("area_mm2")),
                      num(vs), num(ratio, "%.6f"), note])
        if arm == "J":
            ch = None
            for o in rec.get("objs", []):
                if o.get("path") == rec.get("obj_chosen"):
                    ch = o
            derive.append([piece, rec.get("pcd_md5"), rec.get("n_points"),
                           rec.get("header_points"), rec.get("recorded_points"),
                           num(rec.get("count_matches_record")),
                           os.path.basename(ch["path"]) if ch else "na",
                           ch["n_verts"] if ch else "na", ch["n_faces"] if ch else "na",
                           num(ch["max_delta_vs_cloud_mm"] if ch else None),
                           num(rec.get("area_mm2"))])
    w(os.path.join(out, "sizes32.tsv"),
      ["piece", "arm", "n_points", "extent_mm", "area_mm2", "vessel_mm", "ratio", "note"],
      sizes)
    w(os.path.join(out, "derive32.tsv"),
      ["piece", "pcd_md5", "pcd_points", "header_points", "recorded_points",
       "count_matches_record", "obj_used", "obj_verts", "obj_faces",
       "max_delta_vs_cloud_mm", "area_mm2"], derive)
    vrows = []
    for pot in ("Juglet", "PotA"):
        rec = vessel.get(pot)
        if rec is None:
            vrows.append([pot, "na", "na", "na", "na", "na", "na", "na", "na", "na",
                          "na", "na", "missing cell A_VESSEL_%s" % pot])
            continue
        for mode in ("Rp+t", "pR+t", "inv"):
            pm = rec["per_mode"][mode]
            ms = rec["mate_check"] if mode == rec["mode_selected"] else {}
            vrows.append([pot, mode, num(pm["diag_mm"]),
                          num(pm["sides_mm"][0]), num(pm["sides_mm"][1]),
                          num(pm["sides_mm"][2]),
                          "yes" if mode == rec["mode_selected"] else "no",
                          num(ms.get("mate_min_median_mm")),
                          num(ms.get("mate_min_max_mm")),
                          num(ms.get("nonmate_min_median_mm")),
                          num(ms.get("n_pieces_whose_closest_is_a_mate")),
                          num(rec["vessel_mm"]) if mode == rec["mode_selected"] else "",
                          "n_pieces=%d; selected=%s (%s); mate test on the selected "
                          "convention only" % (rec["n_pieces"], rec["mode_selected"],
                                               rec["mode_selected_by"])])
    w(os.path.join(out, "vessel32.tsv"),
      ["pot", "mode", "diag_mm", "side_x_mm", "side_y_mm", "side_z_mm", "chosen",
       "mate_min_median_mm", "mate_min_max_mm", "nonmate_min_median_mm",
       "n_closest_is_mate", "vessel_mm", "note"], vrows)
    grows, sweep, anchors, wrows = [], [], [], []
    for arm, key, piece in ARMS:
        rec, why = load(out, "B_%s_%s" % (arm, key))
        for wm in WINDOWS:
            if rec is None:
                wrows.append([piece, arm, wm, "na", "na", "na", "na", "na", "na", "na",
                              "na", "na", why, "na", "na", "na", "na", "na"])
                continue
            d = rec["windows"][wm]
            notes = []
            if d["rho_median_mm"] is None:
                notes.append("no centre had >=%d neighbours in this window"
                             % 6)
            if d["angle_p50_deg"] is None:
                notes.append("no pairs in this window")
            notes.append("n_centres=%d; n_pairs=%d; n_capped=%d; ang_step=%.3f deg; "
                         "noise floor per (piece,arm), not per window"
                         % (d["n_centres"], d["n_pairs"], d["n_centres_capped"],
                            rec["ang_step_deg"]))
            wrows.append([piece, arm, wm, num(d["n_nb_median"], "%.1f"),
                          num(d["rho_median_mm"], "%.4f"), num(d["rho_p25_mm"], "%.4f"),
                          num(d["rho_p75_mm"], "%.4f"), num(d["share_at_cap"], "%.4f"),
                          num(d["angle_p50_deg"], "%.3f"),
                          num(d["angle_p10_deg"], "%.3f"),
                          num(d["angle_p90_deg"], "%.3f"),
                          num(rec["noise_floor_deg"], "%.3f"),
                          "; ".join(notes), num(rec["n_points"]),
                          num(d["n_pairs"]), num(d["n_fit"]),
                          num(d["share_gt90"], "%.4f"),
                          num(rec["spacing_median_mm"], "%.4f")])
    w(os.path.join(out, "windows32.tsv"),
      ["piece", "arm", "window_mm", "n_neighbours_median", "rho_median_mm",
       "rho_p25_mm", "rho_p75_mm", "share_at_cap", "angle_p50_deg", "angle_p10_deg",
       "angle_p90_deg", "noise_floor_deg", "note", "n_points", "n_pairs", "n_fit",
       "share_gt90", "spacing_median_mm"], wrows)
    for arm, key in DCELLS:
        rec, why = load(out, "D_%s_%s" % (arm, key))
        if rec is None:
            grows.append(["na", arm, key, "na", "na", "na", "na", "na", "na", "na",
                          "na", "na", "na", why])
            continue
        grows.append([rec["piece"], arm, rec["n_points"], rec["curv_k"],
                      rec["regions_before_floor"], num(rec["regions_per_point"]),
                      rec["largest_size"], num(rec["largest_frac_of_cloud"]),
                      rec["n_ge_50"], rec["fail_angle_total"],
                      num(rec["fail_angle_per_point"]), rec["fail_curv_total"],
                      "theta=%.2f kappa=%.2f nb=%d" % (rec["theta_deg"], rec["kappa"],
                                                       rec["nb"]),
                      rec["src"]])
        for fl in ("50", "40", "30", "20", "10"):
            d = rec["floors"][fl]
            sweep.append([rec["piece"], arm, fl, d["n_survive"], num(d["largest_size"]),
                          num(d["largest_frac_of_cloud"]), num(d.get("extent_mm"), "%.4f"),
                          num(d.get("coverage_2mm"), "%.6f"),
                          num(d.get("median_mesh_angle_deg"), "%.3f"),
                          "coverage = fraction of the cloud within %.1f mm of the "
                          "largest survivor; angle = median folded angle of its points "
                          "to the nearest mesh vertex normal" % 2.0])
        if rec.get("anchor"):
            for fld, pair in rec["anchor"]["got"].items():
                anchors.append([arm, rec["piece"], fld, json.dumps(pair[0]),
                                json.dumps(pair[1]), rec["anchor"]["verdict"]])
        if rec.get("e_row"):
            e = rec["e_row"]
            for fld in ("npts", "regions", "largest"):
                anchors.append([arm, rec["piece"], "E_" + fld, json.dumps(e["expected"][fld]),
                                json.dumps(e["got"][fld]),
                                "MATCH" if e["expected"][fld] == e["got"][fld]
                                else "MISMATCH"])
    w(os.path.join(out, "growth32.tsv"),
      ["piece", "arm", "n_points", "curv_k", "regions_before_floor", "regions_per_point",
       "largest_size", "largest_frac_of_cloud", "n_ge_50", "fail_angle_total",
       "fail_angle_per_point", "fail_curv_total", "settings", "src"], grows)
    w(os.path.join(out, "floorsweep32.tsv"),
      ["piece", "arm", "floor", "n_survive", "largest_size", "largest_frac_of_cloud",
       "extent_mm", "coverage_2mm", "median_mesh_angle_deg", "note"], sweep)
    w(os.path.join(out, "anchors32.tsv"),
      ["arm", "piece", "field", "expected", "got", "verdict"], anchors)
    idx = []
    cd = os.path.join(out, "cells")
    for fn in sorted(os.listdir(cd)) if os.path.isdir(cd) else []:
        if fn.endswith(".json"):
            p = os.path.join(cd, fn)
            idx.append([fn, os.path.getsize(p), io32.md5_file(p)])
    w(os.path.join(out, "cells", "index.tsv"), ["cell", "bytes", "md5"], idx)
    for r in sizes:
        print("[T32] sizes %s" % "\t".join(str(x) for x in r[:7]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
