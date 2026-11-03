set -uo pipefail
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1733_45ba206_t69-axis-corpus
cd $RUN/out && tar czf /tmp/t69A.tgz *.tsv && cd - >/dev/null
md5sum /tmp/t69A.tgz
base64 -w0 /tmp/t69A.tgz | head -c 100
echo
ls -l /tmp/t69A.tgz
