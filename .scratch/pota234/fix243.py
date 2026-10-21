p = 'C:/PR/SfSpp_preprocessing/.scratch/pota234/patch234d.py'
L = open(p, encoding='utf-8').read().split('\n')
assert 'paperRule, planeJoinDeg' in L[242], L[242][:60]
L[242:244] = [
 'once("            paperChain, paperTheta, paperKappa, paperNB, paperCloseMM, paperPatchDeg, paperCurvRel);",',
 '     "            paperChain, paperTheta, paperKappa, paperNB, paperRhoD, paperRhoN, paperRhoC, paperRhoInN, paperRhoInC);")',
]
open(p, 'w', encoding='utf-8').write('\n'.join(L))
print('fixed')
