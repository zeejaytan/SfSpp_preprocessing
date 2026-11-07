import glob
import os

runs = [
    '20261107-0420_e4329a7_t314b-kladder-E',
    '20261107-0420_e4329a7_t314c-potd',
    '20261107-0420_e4329a7_t314c-poti',
    '20261107-0420_e4329a7_t314c-pota',
    '20261107-0420_e4329a7_t314c-potb',
    '20261107-0420_e4329a7_t314c-potg',
]

for r_name in runs:
    r = f'/data/gpfs/projects/punim2657/SfSpp/runs/{r_name}'
    tag = r_name.split('_')[-1]
    print(f"=== {tag} ===")
    if not os.path.exists(r):
        print("  DOES NOT EXIST")
        continue
    # Check log files in logs/
    for lf in sorted(glob.glob(f'{r}/logs/*')):
        name = os.path.basename(lf)
        sz = os.path.getsize(lf)
        with open(lf, 'r', errors='ignore') as fp:
            lines = [l.strip() for l in fp if l.strip()]
        last = lines[-1] if lines else '<empty>'
        # For active arm logs, print last 2 lines
        if 'E_' in name or 'MM' in name or 'MO' in name or 'slurm' in name:
            last2 = ' /// '.join(lines[-2:]) if len(lines) >= 2 else last
            print(f"  {name:25s} ({sz:8d} B): {last2[:120]}")
    # Check score/
    if os.path.exists(f'{r}/score'):
        for sf in sorted(glob.glob(f'{r}/score/*')):
            sname = os.path.basename(sf)
            if sname.endswith('.tsv') or sname.endswith('.txt'):
                with open(sf, 'r', errors='ignore') as fp:
                    content = fp.read().strip().replace('\n', ' | ')
                print(f"  SCORE {sname}: {content[:150]}")
