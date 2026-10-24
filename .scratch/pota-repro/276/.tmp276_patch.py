
import io, sys
P = r"C:/PR/worktrees/sfs/276/mesh_processing_headless.cpp"
H = open(r"C:/PR/worktrees/sfs/276/.tmp276_helpers.cpp", encoding="utf-8").read()
if not H.endswith("\n"): H += "\n"

raw = open(P, newline="", encoding="utf-8", errors="surrogateescape").read()
crlf = "\r\n" in raw
s = raw.replace("\r\n", "\n")

a1 = "void surfaceSegmentation(std::string filePath, int minCluster, int noOfNeighbours, double smoothnessAngleThreshold, double curvatureThreshold,"
assert s.count(a1) == 1, ("a1", s.count(a1))

a2 = ('        if (paperChain) {\n'
      '            std::cout << "Calling mergePaper234 function." << std::endl;\n'
      '            mergePaper234(cloud, normals, clusters, paperRhoD, paperRhoN, paperRhoC, paperRhoInN, paperRhoInC, 10, 30);\n'
      '            std::sort(clusters.begin(), clusters.end(), myobject3);\n'
      '            classifyAndOrderPaper234(cloud, normals, clusters);\n'
      '        } else {\n')
assert s.count(a2) == 1, ("a2", s.count(a2))

b2 = ('        if (paperChain) {\n'
      '            std::cout << "Calling mergePaper234 function." << std::endl;\n'
      '            // TICKET 276: SFS_MERGE_DIAG unset/0 -> mdiag276 is empty and nothing below runs.\n'
      '            const std::string mdiag276 = mergeDiagMode276();\n'
      '            const bool split276 = (mdiag276 == "split");\n'
      '            const int nBeforeSplit276 = static_cast<int>(clusters.size());\n'
      '            std::vector<char> half276;\n'
      '            if (split276) splitLargestCluster276(cloud, clusters, half276);\n'
      '            mergePaper234(cloud, normals, clusters, paperRhoD, paperRhoN, paperRhoC, paperRhoInN, paperRhoInC, 10, 30);\n'
      '            std::sort(clusters.begin(), clusters.end(), myobject3);\n'
      '            classifyAndOrderPaper234(cloud, normals, clusters);\n'
      '            if (split276) reportSplit276(half276, clusters, nBeforeSplit276);\n'
      '            if (!mdiag276.empty()) dumpMergeDiag276(cloud, clusters, paperTheta, half276);\n'
      '        } else {\n')

s = s.replace(a1, H + "\n" + a1, 1)
s = s.replace(a2, b2, 1)
if crlf: s = s.replace("\n", "\r\n")
open(P, "w", newline="", encoding="utf-8", errors="surrogateescape").write(s)
print("patched crlf=%s bytes=%d" % (crlf, len(s)))
