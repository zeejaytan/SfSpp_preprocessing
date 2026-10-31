import glob
ids = ["155","173","174","175","177","179","199","221","222","223","224","225","226","227","228","229","230","231","232"]
note = open('.scratch/_note.txt', encoding='utf-8').read()
done = []
for i in ids:
    for p in glob.glob('.scratch/pota-repro/issues/' + i + '-*.md'):
        txt = open(p, encoding='utf-8').read()
        if 'Evidence-path note (2026-10-23)' in txt:
            print('ALREADY', p); continue
        open(p, 'a', encoding='utf-8').write(note); done.append(p)
print('annotated', len(done))
for p in done: print(' ', p)