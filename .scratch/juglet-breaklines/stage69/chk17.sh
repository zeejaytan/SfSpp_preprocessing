B=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0734_601013e_t69-density-panel
grep -n 'SBATCH --time\|SBATCH --mem\|SBATCH --cpus' $B/submit.sbatch
echo '--- start time ---'; head -3 $B/logs/slurm-34274535.out
echo '--- pota/ potc durations from piece dirs mtimes ---'; ls -ld --time-style=+%H:%M $B/out_pota/pieces/*/ $B/out_potc/pieces/*/ 2>/dev/null | head -4
ls -ld --time-style=+%H:%M $B/out_potd/pieces/*/ 2>/dev/null
