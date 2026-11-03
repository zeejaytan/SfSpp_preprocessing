T=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1429_3b3efbc_t67-juglet-assembly
echo '--- PACTL ---'; cat $T/out/PACTL/'1. Acc.txt' 2>/dev/null | head -5
echo '--- APA ---'; cat $T/out/APA/'1. Acc.txt' 2>/dev/null | head -5
echo '--- A20 ---'; cat $T/out/A20/'1. Acc.txt' 2>/dev/null | head -5
echo '--- t68 GPA50 ---'; cat /data/gpfs/projects/punim2657/SfSpp/runs/20261103-1523_4b516be_t68-axis-method/guard68/out/GPA50/'1. Acc.txt' 2>/dev/null | head -5
