path = '/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv'
with open(path) as f:
    lines = f.readlines()
new_lines = []
for line in lines:
    parts = line.rstrip('\r\n').split('\t')
    while len(parts) < 6:
        parts.append('')
    if parts[1] == '34463442':
        parts[4] = 'pass'
        parts[5] = 'K3 reached 26/31 (83.9%) and 44/62 joins (71.0%); K6 suffered decoy dilution (22/31, 14/31)'
    new_lines.append('\t'.join(parts) + '\n')
with open(path, 'w') as f:
    f.writelines(new_lines)
print('Updated runs/index.tsv for job 34463442 successfully')
