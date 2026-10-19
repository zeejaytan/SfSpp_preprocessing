W="/data/gpfs/projects/punim2657/sfs_cure_1c6a8f9/original_nurbs_preprocessing/mesh_processing_headless.cpp"
src=open(W).read()
anchor="        if (clusters.size() > 1)\n        {\n            auto& largestCluster = clusters[0];"
assert src.count(anchor)==1, ("anchor count", src.count(anchor))
block=open("/tmp/p174_block.txt").read()
open(W,"w").write(src.replace(anchor, block+anchor))
print("PATCHED")
