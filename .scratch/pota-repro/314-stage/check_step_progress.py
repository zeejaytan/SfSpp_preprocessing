import glob
import os
import re

runs = [
    ('Pot E', '/data/gpfs/projects/punim2657/SfSpp/runs/20261107-0420_e4329a7_t314b-kladder-E'),
    ('Pot D', '/data/gpfs/projects/punim2657/SfSpp/runs/20261107-0420_e4329a7_t314c-potd'),
    ('Pot I', '/data/gpfs/projects/punim2657/SfSpp/runs/20261107-0420_e4329a7_t314c-poti'),
    ('Pot A', '/data/gpfs/projects/punim2657/SfSpp/runs/20261107-0420_e4329a7_t314c-pota'),
]

for label, r in runs:
    bin_logs = sorted(glob.glob(f'{r}/work/logs/binary_*.log'))
    for bl in bin_logs:
        name = os.path.basename(bl)
        with open(bl, 'r', errors='ignore') as f:
            content = f.read()
        steps = re.findall(r'-----\s*Start\s*:\s*(\d+)\s*Step\s*-----', content)
        acc = re.findall(r'Edge accuracy\s*:\s*(\d+)\s*/\s*(\d+)', content)
        last_step = steps[-1] if steps else 'N/A'
        last_acc = f"{acc[-1][0]}/{acc[-1][1]}" if acc else 'in progress'
        done = "FINISHED" if "Result save finish" in content else "RUNNING"
        print(f"{label:6s} | {name:20s} | Step {last_step:>2s} | Acc: {last_acc} | {done}")
