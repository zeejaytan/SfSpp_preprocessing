import shutil
shutil.copy('C:/PR/SfSpp_preprocessing/.scratch/pota234/mesh_orig_main.cpp', 'C:/PR/SfSpp_preprocessing/.scratch/pota234/chaincheck_tmp.cpp')
for s in ['patch234.py', 'patch234b.py', 'patch234c.py', 'patch234d.py']:
    src = open('C:/PR/SfSpp_preprocessing/.scratch/pota234/' + s, encoding='utf-8').read()
    src = src.replace('C:/PR/SfSpp_preprocessing/.scratch/pota234/mesh_processing_headless.cpp', 'C:/PR/SfSpp_preprocessing/.scratch/pota234/chaincheck_tmp.cpp')
    exec(compile(src, s, 'exec'))
a = open('C:/PR/SfSpp_preprocessing/.scratch/pota234/chaincheck_tmp.cpp','rb').read()
b = open('C:/PR/SfSpp_preprocessing/.scratch/pota234/mesh_processing_headless.cpp','rb').read()
print('chain-repro match:', a == b, len(a), len(b))
