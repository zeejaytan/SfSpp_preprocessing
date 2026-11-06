import numpy as np

def parse_T(path):
    with open(path) as f:
        toks = f.read().split()
    vals = [float(x) for x in toks[:16]]
    return np.array(vals, dtype=float).reshape(4, 4)

# Let's inspect E_K1R2_cpp.json which is locally fetched in C:/PR/SfSpp_preprocessing/artifacts/pota311/stageB/E_K1R2_cpp.json
import json
with open('C:/PR/SfSpp_preprocessing/artifacts/pota311/stageB/E_K1R2_cpp.json') as f:
    d = json.load(f)
print("E_K1R2 joins passed:", d.get("n_joins_passed"), "sherds passed:", d.get("n_sherds_passed"))
