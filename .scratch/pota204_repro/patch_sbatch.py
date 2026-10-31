import re
p = '/data/gpfs/projects/punim2657/pota204_repro/run_pota204_stage_AC.sbatch'
s = open(p).read()
s = s.replace('# POTA-204 STAGE: PRISTINE Pot C E2E (204-dot TRUE thin-loop Bl_0 on PRISTINE fresh', '# POTA-204 STAGE: PRISTINE Pot C E2E (D-all: 4x TRUE thin-loop Bl_0 C01-C04 on PRISTINE fresh')
s = s.replace('C_FRESH="${P204}/pota204_prep/pota204_bundle_C/SfS_pp"', 'C_FRESH="/data/gpfs/projects/punim2657/pota197_repro/pota197_prep/pota197_bundle_C/SfS_pp"')
s = s.replace('C_FRESH_MD5="${P204}/pota204_prep/pota204_C_bun_md5.txt"', 'C_FRESH_MD5="/data/gpfs/projects/punim2657/pota197_repro/pota197_prep/pota197_C_bun_md5.txt"')
s = s.replace('rims_C197/', 'rims_C204/')
open(p, 'w').write(s)
print('patched')
