import glob
import os

runs = [
    ('Pot E', '/data/gpfs/projects/punim2657/SfSpp/runs/20261107-0420_e4329a7_t314b-kladder-E'),
    ('Pot D', '/data/gpfs/projects/punim2657/SfSpp/runs/20261107-0420_e4329a7_t314c-potd'),
    ('Pot I', '/data/gpfs/projects/punim2657/SfSpp/runs/20261107-0420_e4329a7_t314c-poti'),
    ('Pot A', '/data/gpfs/projects/punim2657/SfSpp/runs/20261107-0420_e4329a7_t314c-pota'),
]

for label, r in runs:
    print(f"==================================================")
    print(f"=== {label}: {r}")
    print(f"==================================================")
    bin_logs = sorted(glob.glob(f'{r}/work/logs/binary_*.log'))
    if not bin_logs:
        # maybe under logs/ ?
        bin_logs = sorted(glob.glob(f'{r}/logs/binary_*.log'))
    for bl in bin_logs:
        name = os.path.basename(bl)
        sz = os.path.getsize(bl)
        with open(bl, 'r', errors='ignore') as f:
            lines = [l.strip() for l in f if l.strip()]
        total_lines = len(lines)
        # Find step progress if any
        step_lines = [l for l in lines if 'Step' in l or 'step' in l or 'accuracy' in l or 'Accuracy' in l or 'Iteration' in l or 'Candidate' in l or 'Sherd' in l]
        last_steps = step_lines[-3:] if step_lines else []
        last_any = lines[-2:] if lines else ['<empty>']
        print(f"  [{name}] ({sz} bytes, {total_lines} lines):")
        for s in last_steps:
            print(f"     [STEP] {s}")
        for a in last_any:
            print(f"     [TAIL] {a}")
