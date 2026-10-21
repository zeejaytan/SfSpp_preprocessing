p = 'C:/PR/SfSpp_preprocessing/.scratch/pota234/run234.sbatch'
t = open(p, encoding='utf-8').read()
a = '  export SFS_PAPER_CLOSE_MM="${SFS_PAPER_CLOSE_MM:-3.0}" SFS_PAPER_PATCH_DEG="${SFS_PAPER_PATCH_DEG:-15.0}" SFS_PAPER_CURV_REL="${SFS_PAPER_CURV_REL:-0.30}"'
assert t.count(a) == 1
t = t.replace(a, '  export SFS_PAPER_RHOD="${SFS_PAPER_RHOD:-1.0}" SFS_PAPER_RHON="${SFS_PAPER_RHON:-0.95}" SFS_PAPER_RHOC="${SFS_PAPER_RHOC:-0.1}" SFS_PAPER_RHOINN="${SFS_PAPER_RHOINN:-0.75}" SFS_PAPER_RHOINC="${SFS_PAPER_RHOINC:-0.25}"')
b = 'SFS_PAPER_CLOSE_MM="${SFS_PAPER_CLOSE_MM:-}" SFS_PAPER_PATCH_DEG="${SFS_PAPER_PATCH_DEG:-}" SFS_PAPER_CURV_REL="${SFS_PAPER_CURV_REL:-}"' 
assert t.count(b) == 1
t = t.replace(b, 'SFS_PAPER_RHOD="${SFS_PAPER_RHOD:-}" SFS_PAPER_RHON="${SFS_PAPER_RHON:-}" SFS_PAPER_RHOC="${SFS_PAPER_RHOC:-}" SFS_PAPER_RHOINN="${SFS_PAPER_RHOINN:-}" SFS_PAPER_RHOINC="${SFS_PAPER_RHOINC:-}"')
open(p, 'w', encoding='utf-8').write(t)
print('sbatch ok')
