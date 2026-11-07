import os
import shutil

run_tag = '20261107-0415_e4329a7_t314a-axes'
run_dir = f'/data/gpfs/projects/punim2657/SfSpp/runs/{run_tag}'
os.makedirs(f'{run_dir}/logs', exist_ok=True)
os.makedirs(f'{run_dir}/out', exist_ok=True)
os.makedirs(f'{run_dir}/work', exist_ok=True)

# Copy sfs_axes
dst_axes = f'{run_dir}/work/sfs_axes'
if os.path.exists(dst_axes):
    shutil.rmtree(dst_axes)
shutil.copytree('/data/gpfs/projects/punim2657/sfs_preprocessing/work_314/sfs_axes', dst_axes)

# Copy generate_axes313.py as generate_axes314.py
src_gen = '/data/gpfs/projects/punim2657/SfSpp/runs/20261106-1316_fe906ab_t313a-axes/work/generate_axes313.py'
with open(src_gen) as f:
    c = f.read()
c = c.replace('axes313', 'axes314')
with open(f'{run_dir}/work/generate_axes314.py', 'w') as f:
    f.write(c)

with open(f'{run_dir}/run.json', 'w') as f:
    f.write('''{
  "runid": "%s",
  "ticket": "314",
  "stage": "A/B: Axes generation for Pots A, B, D, E, G, I",
  "commit": "e4329a7",
  "pots": ["A", "B", "D", "E", "G", "I"],
  "out": "%s/out/axes314"
}
''' % (run_tag, run_dir))

print('Successfully setup', run_dir)
