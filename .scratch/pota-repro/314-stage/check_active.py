import glob
import os

def check_tails():
    # 1. Pot E
    r_e = '/data/gpfs/projects/punim2657/SfSpp/runs/20261107-0420_e4329a7_t314b-kladder-E'
    print("=== POT E ACTIVE ===")
    for arm in ['E_K3R1', 'E_K3R2', 'E_K6R1', 'E_K6R2']:
        lf = f'{r_e}/logs/run_{arm}.log'
        if os.path.exists(lf):
            with open(lf, 'r', errors='ignore') as f:
                lines = [l.strip() for l in f if l.strip()]
            print(f"  {arm} ({len(lines)} lines):")
            for l in lines[-4:]:
                print(f"    {l}")
        else:
            print(f"  {arm}: log does not exist yet")

    # 2. Pot D
    r_d = '/data/gpfs/projects/punim2657/SfSpp/runs/20261107-0420_e4329a7_t314c-potd'
    print("\n=== POT D ACTIVE ===")
    for arm in ['MMR1', 'MMR2']:
        lf = f'{r_d}/logs/run_{arm}.log'
        if os.path.exists(lf):
            with open(lf, 'r', errors='ignore') as f:
                lines = [l.strip() for l in f if l.strip()]
            print(f"  {arm} ({len(lines)} lines):")
            for l in lines[-4:]:
                print(f"    {l}")

    # 3. Pot I
    r_i = '/data/gpfs/projects/punim2657/SfSpp/runs/20261107-0420_e4329a7_t314c-poti'
    print("\n=== POT I ACTIVE ===")
    for arm in ['MMR1', 'MMR2']:
        lf = f'{r_i}/logs/run_{arm}.log'
        if os.path.exists(lf):
            with open(lf, 'r', errors='ignore') as f:
                lines = [l.strip() for l in f if l.strip()]
            print(f"  {arm} ({len(lines)} lines):")
            for l in lines[-4:]:
                print(f"    {l}")

    # 4. Pot A resumed
    r_a = '/data/gpfs/projects/punim2657/SfSpp/runs/20261107-0420_e4329a7_t314c-pota'
    print("\n=== POT A RESUMED ===")
    slurm_logs = sorted(glob.glob(f'{r_a}/logs/slurm-34467975.*'))
    for sl in slurm_logs:
        print(f"  {os.path.basename(sl)}:")
        with open(sl, 'r', errors='ignore') as f:
            lines = [l.strip() for l in f if l.strip()]
        for l in lines[-4:]:
            print(f"    {l}")
    for arm in ['MMR1', 'MMR2']:
        lf = f'{r_a}/logs/run_{arm}.log'
        if os.path.exists(lf):
            with open(lf, 'r', errors='ignore') as f:
                lines = [l.strip() for l in f if l.strip()]
            print(f"  {arm} ({len(lines)} lines):")
            for l in lines[-4:]:
                print(f"    {l}")

if __name__ == '__main__':
    check_tails()
