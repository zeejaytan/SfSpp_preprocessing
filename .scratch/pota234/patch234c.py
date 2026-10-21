"""T234 paper arm v2: grow angle reference = current front point (Rabbani [35] /
PCL semantics), not the fixed region seed. v1's fixed-seed reference
over-segmented (P12: 85 grow clusters); the reference must drift with the
front so gradual twist is followed and only sharp turns split."""
SRC = "C:/PR/SfSpp_preprocessing/.scratch/pota234/mesh_processing_headless.cpp"

with open(SRC, "rb") as f:
    txt = f.read().replace(b"\r\n", b"\n").decode("utf-8", errors="surrogateescape")

def once(old, new):
    global txt
    n = txt.count(old)
    assert n == 1, f"anchor x{n}: {old[:70]!r}"
    txt = txt.replace(old, new)

once("// (1) region growing from the min-curvature point: n_b neighbours, join iff\n// curvature < tau_kappa AND normal angle to the REGION SEED normal < tau_theta.",
     "// (1) region growing from the min-curvature point: n_b neighbours, join iff\n// curvature < tau_kappa AND normal angle to the CURRENT front-point normal\n// < tau_theta (Rabbani [35] / PCL semantics: the reference drifts with the\n// front, so gradual twist is followed and only sharp turns split; a fixed\n// seed reference over-segments -- verified v1 vs v2).")
once("        Eigen::Vector3f seedN(pnormals->points[sd].normal_x,\n                              pnormals->points[sd].normal_y,\n                              pnormals->points[sd].normal_z);\n        Eigen::Vector4f seedN4(seedN(0), seedN(1), seedN(2), 0.0f);\n        pfront.clear();",
     "        pfront.clear();")
once("            int cf = pfront[fh2++];\n            pnb.clear(); pdist.clear();",
     "            int cf = pfront[fh2++];\n            Eigen::Vector4f curN4(pnormals->points[cf].normal_x,\n                                  pnormals->points[cf].normal_y,\n                                  pnormals->points[cf].normal_z, 0.0f);\n            pnb.clear(); pdist.clear();")
once("                if (pcl::getAngle3D(seedN4, nn4, true) > thetaDeg) continue;",
     "                if (pcl::getAngle3D(curN4, nn4, true) > thetaDeg) continue;")

with open(SRC, "wb") as f:
    f.write(txt.encode("utf-8", errors="surrogateescape"))
print("patch234c OK, bytes:", len(txt))
