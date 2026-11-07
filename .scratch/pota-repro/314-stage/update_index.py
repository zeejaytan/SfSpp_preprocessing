path = '/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv'
with open(path) as f:
    lines = f.readlines()
new_lines = []
for line in lines:
    parts = line.rstrip('\r\n').split('\t')
    while len(parts) < 6:
        parts.append('')
    jobid = parts[1]
    if jobid == '34459615':
        parts[4] = 'pass'
        parts[5] = '120 piece candidates generated across 6 pots'
    elif jobid == '34463452':
        parts[4] = 'pass'
        parts[5] = '9/9 sherds (15/15 joins, 100%) zero regression across all 4 arms'
    elif jobid == '34463454':
        parts[4] = 'pass'
        parts[5] = '7/7 sherds (10/10 joins, 100%) zero regression across all 4 arms'
    elif jobid == '34463453':
        parts[4] = 'timeout'
        parts[5] = 'MOR1/2 23/28 (55/69, 79.7%); MMR timed out at 6h at Step 6'
    elif jobid == '34463455':
        parts[4] = 'timeout'
        parts[5] = 'MOR1/2 25/26 (59/62, 95.2%); MMR timed out at 6h at Step 11'
    new_lines.append('\t'.join(parts) + '\n')

new_lines.append('20261107-0420_e4329a7_t314c-pota\t34467975\te4329a7\tt314c-pota-mmr\tpass\t8/8 sherds (15/15 joins, 100%) seated with P08\n')

with open(path, 'w') as f:
    f.writelines(new_lines)
print('Updated runs/index.tsv successfully')
