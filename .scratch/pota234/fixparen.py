p = 'C:/PR/SfSpp_preprocessing/.scratch/pota234/patch234d.py'
L = open(p, encoding='utf-8').read().split('\n')
assert L[225].rstrip().endswith('0.25")'), L[225][-40:]
L[225] = L[225].replace('0.25")', '0.25)")')
open(p, 'w', encoding='utf-8').write('\n'.join(L))
print('script fixed')
q = 'C:/PR/SfSpp_preprocessing/.scratch/pota234/mesh_processing_headless.cpp'
M = open(q, encoding='utf-8').read().split('\n')
hit = [i for i, l in enumerate(M) if 'double paperRhoInC = 0.25' in l]
print('mesh hits:', hit)
for i in hit:
    assert M[i].rstrip().endswith('0.25'), repr(M[i][-20:])
    M[i] = M[i].rstrip() + ')'
open(q, 'w', encoding='utf-8').write('\n'.join(M))
print('mesh fixed')
