import glob
import json
import os

sc = '/data/gpfs/projects/punim2657/SfSpp/runs/20261107-0420_e4329a7_t314b-kladder-E/score'
arms = ['E_MOR1', 'E_MOR2', 'E_BASER1', 'E_BASER2', 'E_K1R1', 'E_K1R2', 'E_K2R1', 'E_K2R2', 'E_K3R1', 'E_K3R2']

print(f"{'Arm':10s} | {'Sherds':8s} | {'Joins':8s} | {'Sherd %':8s} | {'Edge %':8s} | Failed Pieces")
print('-' * 85)
for a in arms:
    json_file = f'{sc}/{a}_cpp.json'
    if os.path.exists(json_file):
        with open(json_file) as f:
            d = json.load(f)
        sherd = f"{d['n_sherd']}/{d['total_sherd']}"
        edge = f"{d['n_join']}/{d['total_join']}"
        sherd_pct = f"{100.0 * d['n_sherd'] / d['total_sherd']:.1f}%"
        edge_pct = f"{100.0 * d['n_join'] / d['total_join']:.1f}%"
        failed = str(d.get('failed_pieces', []))
        print(f"{a:10s} | {sherd:8s} | {edge:8s} | {sherd_pct:8s} | {edge_pct:8s} | {failed}")
