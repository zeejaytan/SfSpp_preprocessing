RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0729_ae5ad59_t69-density-panel
echo '--- slurm out ---'; cat $RUN/logs/slurm-34274349.out
echo '--- binaries ---'; cat $RUN/binaries.md5 2>/dev/null
echo '--- proof dir ---'; ls -la $RUN/proof 2>/dev/null
echo '--- proof mesh tail ---'; tail -5 $RUN/proof/mesh.log 2>/dev/null
echo '--- proof edge logs ---'; ls -la $RUN/proof/*.log 2>/dev/null
echo '--- date ---'; date
