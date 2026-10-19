import sys
p = "/data/gpfs/projects/punim2657/sfs_cure_1c6a8f9/original_nurbs_preprocessing/edgeline_extraction_headless.cpp"
src = open(p).read()
old1 = "\tsize_t faceVetoKept = 0, faceVetoDropped = 0;"
new1 = ("\t// POTA174-NOVETO (lead steer 2026-10-20: veto dropped entirely). Env-gated: SFS_NOVETO=1\n"
        "\t// forces threshold 2 (align is a cosine, always <=2) so every admitted dot is kept.\n"
        "\t// Unset/0 = cure veto behavior preserved.\n"
        "\tif (const char* p174nv = std::getenv(\"SFS_NOVETO\")) { if (*p174nv && std::string(p174nv) != \"0\") { faceVetoThresh = 2.0f; std::cout << \"[POTA174-NOVETO] face veto disabled (thr=2, keep all)\" << std::endl; } }\n"
        "\tsize_t faceVetoKept = 0, faceVetoDropped = 0;")
assert src.count(old1) == 1, "anchor1 count=%d" % src.count(old1)
src = src.replace(old1, new1)
old2 = ("\tif (cloud_filtered->points.empty()) {\n"
        "\t\tstd::cout << \"[SFS-T05] filter emptied the cloud -- sequencing UNFILTERED boundary (loud fallback)\" << std::endl;\n"
        "\t\t*cloud_to_sequence = *boundaryCloud_Improved;\n"
        "\t} else {\n"
        "\t\t*cloud_to_sequence = *cloud_filtered;\n"
        "\t}")
new2 = ("\tbool p174noveto = false;\n"
        "\tif (const char* p174nv2 = std::getenv(\"SFS_NOVETO\")) { p174noveto = (*p174nv2 && std::string(p174nv2) != \"0\"); }\n"
        "\tif (p174noveto) {\n"
        "\t\tstd::cout << \"[POTA174-NOVETO] T05 bypass -- sequencing UNFILTERED boundary\" << std::endl;\n"
        "\t\t*cloud_to_sequence = *boundaryCloud_Improved;\n"
        "\t}\n"
        "\telse if (cloud_filtered->points.empty()) {\n"
        "\t\tstd::cout << \"[SFS-T05] filter emptied the cloud -- sequencing UNFILTERED boundary (loud fallback)\" << std::endl;\n"
        "\t\t*cloud_to_sequence = *boundaryCloud_Improved;\n"
        "\t} else {\n"
        "\t\t*cloud_to_sequence = *cloud_filtered;\n"
        "\t}")
assert src.count(old2) == 1, "anchor2 count=%d" % src.count(old2)
src = src.replace(old2, new2)
open(p, "w").write(src)
print("PATCH OK")
