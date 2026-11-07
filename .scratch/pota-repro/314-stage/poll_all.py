import os
import glob
import subprocess

runs = [
    '20261107-0420_e4329a7_t314b-kladder-E',
    '20261107-0420_e4329a7_t314c-pota',
    '20261107-0420_e4329a7_t314c-potb',
    '20261107-0420_e4329a7_t314c-potd',
    '20261107-0420_e4329a7_t314c-potg',
    '20261107-0420_e4329a7_t314c-poti',
]

job_ids = []
for r in runs:
    p = f'/data/gpfs/projects/punim2657/SfSpp/runs/{r}'
    sbatch_id_path = f'{p}/sbatch.id'
    if os.path.exists(sbatch_id_path):
        with open(sbatch_id_path) as f:
            jid = f.read().strip()
            if jid:
                job_ids.append(jid)

if job_ids:
    cmd = ['sacct', '-j', ','.join(job_ids), '--format=JobID,JobName%15,Partition,AllocCPUS,Elapsed,State,ExitCode']
    res = subprocess.run(cmd, capture_output=True, text=True)
    print("=== SACCT STATUS ===")
    print(res.stdout.strip())
    print()

print("=== LOG PROGRESS ===")
for r in runs:
    p = f'/data/gpfs/projects/punim2657/SfSpp/runs/{r}'
    tag = r.split('_')[-1]
    slurm_logs = glob.glob(f'{p}/logs/slurm-*.out')
    last_line = 'no slurm log'
    if slurm_logs:
        with open(slurm_logs[0]) as f:
            lines = [l.strip() for l in f if l.strip()]
            if lines:
                last_line = lines[-1]
    acc_files = glob.glob(f'{p}/score/*.tsv') + glob.glob(f'{p}/score/*.txt')
    acc_summary = ""
    if os.path.exists(f'{p}/score/acc.tsv'):
        with open(f'{p}/score/acc.tsv') as f:
            acc_summary = f.read().strip().replace('\n', ' | ')
    print(f'[{tag}] {last_line}')
    if acc_summary:
        print(f'   -> acc: {acc_summary}')
