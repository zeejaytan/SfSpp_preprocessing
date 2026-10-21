import re
t = open('C:/PR/SfSpp_preprocessing/.scratch/pota234/sfspp_html.html', encoding='utf-8').read()
# all h2/h1 headings with their positions
heads = [(m.start(), m.group(0)) for m in re.finditer(r'<h[12][^>]*>.*?</h[12]>', t, re.S)]
seg = t[386442:418935]
tx = re.sub(r'<[^>]+>', ' ', seg)
tx = re.sub(r'[ \t\xa0]+', ' ', tx)
tx = re.sub(r'\n\s*\n+', '\n\n', tx)
open('C:/PR/SfSpp_preprocessing/.scratch/pota234/appendixA.txt','w',encoding='utf-8').write(tx)
print('chars:', len(tx))
print(tx[:4500])
