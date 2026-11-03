G=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1523_4b516be_t68-axis-method/guard68/instruments
echo '=== PATCH ==='
base64 -w0 $G/guard68.patch
echo
echo '=== ARM67 ==='
base64 -w0 $G/arm67.sh
echo
