PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
$PY -c 'import matplotlib; print("mpl", matplotlib.__version__)' 2>&1 | tail -2
$PY -c 'import numpy,scipy; print("np",numpy.__version__,"sp",scipy.__version__)' 2>&1 | tail -2
python3 -c 'import matplotlib; print("sys mpl", matplotlib.__version__)' 2>&1 | tail -2
