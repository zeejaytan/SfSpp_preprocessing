#!/usr/bin/env bash
# run ON Spartan.  usage: submitE32.sh <rundir> <tag> <jobname> <walltime> <sha>
# Renders build/submit.sbatch from instruments/submitE.sbatch.tmpl, refuses any unfilled
# placeholder, refuses a carriage return in anything the job will execute (two grids in this
# project died on 'set: pipefail: invalid option name'), then submits from inside the run dir.
set -uo pipefail
RUN=${1:?rundir}
TAG=${2:?tag}
JOBNAME=${3:?jobname}
TIME=${4:?walltime}
SHA=${5:?sha}
RUNID=$(basename "$RUN")
TMPL=$RUN/instruments/submitE.sbatch.tmpl
[ -d "$RUN" ] || { echo "[SUBMIT] FATAL no run dir $RUN"; exit 1; }
[ -f "$RUN/run.json" ] || { echo "[SUBMIT] FATAL no run.json in $RUN"; exit 1; }
[ -f "$TMPL" ] || { echo "[SUBMIT] FATAL no template $TMPL"; exit 1; }
echo "$SHA" | grep -Eq '^[0-9a-f]{40}$' || { echo "[SUBMIT] FATAL sha is not 40 lowercase hex: $SHA"; exit 1; }
echo "[SUBMIT] runid=$RUNID sha=$SHA tag=$TAG template=$(basename "$TMPL") time=$TIME jobname=$JOBNAME"

PYBIN=$(command -v python3 || command -v python || true)
[ -n "$PYBIN" ] || { echo "[SUBMIT] FATAL no python on PATH"; exit 1; }
"$PYBIN" - "$TMPL" "$RUN/submit.sbatch" "$RUN" "$RUNID" "$SHA" "$TAG" "$JOBNAME" "$TIME" <<'PYEOF'
import sys
tmpl, dst, rundir, runid, sha, tag, job, wall = sys.argv[1:9]
s = open(tmpl).read()
for k, v in (("__RUNDIR__", rundir), ("__RUNID__", runid), ("__NEWCOMMIT__", sha),
             ("__IXTAG__", tag), ("__JOBNAME__", job), ("__TIME__", wall)):
    s = s.replace(k, v)
left = [t for t in ("__RUNDIR__", "__RUNID__", "__NEWCOMMIT__", "__IXTAG__",
                    "__JOBNAME__", "__TIME__") if t in s]
if left:
    sys.exit("[SUBMIT] FATAL unfilled placeholder(s): %s" % ",".join(left))
open(dst, "w").write(s)
print("[SUBMIT] wrote %s %d bytes" % (dst, len(s)))
PYEOF
[ $? -eq 0 ] || exit 1
[ -s "$RUN/submit.sbatch" ] || { echo "[SUBMIT] FATAL submit.sbatch missing or empty"; exit 1; }

BAD=0
for f in "$RUN/submit.sbatch" "$RUN"/instruments/*.py "$RUN"/instruments/*.sh "$RUN"/instruments/*.txt "$RUN"/instruments/*.tmpl "$RUN/run.json"; do
  [ -f "$f" ] || continue
  c=$(tr -cd '\015' < "$f" | wc -c)
  if [ "$c" -ne 0 ]; then echo "[SUBMIT] FATAL CRLF in $f ($c CR bytes)"; BAD=1; fi
done
[ "$BAD" -eq 0 ] || exit 1
echo "[SUBMIT] no CRLF in submit.sbatch, instruments, list files or run.json ($(ls "$RUN"/instruments | wc -l) instruments)"

cd "$RUN" || exit 1
sbatch submit.sbatch | tee logs/sbatch.txt
