#!/usr/bin/env bash
# ticket 28: build the run directory of record and submit one job.
# usage: SHA=<commit> GIT7=<git7> submit28.sh <template> <tag> <jobname> <walltime> [KEY=value ...]
# The templates live beside this script; the instruments (stager, replica) are copied
# into <run>/instruments/ so the run directory carries the exact scripts it ran.
set -euo pipefail
TMPL=$1
TAG=$2
JOBNAME=$3
WTIME=$4
shift 4
SRC=$(cd "$(dirname "$0")" && pwd)
case "$TMPL" in /*) ;; *) TMPL=${SRC}/${TMPL} ;; esac
ROOT=/data/gpfs/projects/punim2657/SfSpp/runs
SHA=${SHA:?}
GIT7=${GIT7:?}
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
T25=/data/gpfs/projects/punim2657/SfSpp/runs/20261027-0337_d69f76f_t25-dump-grid2/out/dump
RUNID=$(date +%Y%m%d-%H%M)_${GIT7}_${TAG}
RUN=${ROOT}/${RUNID}
if [ -e "$RUN" ]; then echo "[SUBMIT] FATAL ${RUN} exists"; exit 3; fi
mkdir -p "$RUN/logs" "$RUN/instruments"
cp "$SRC/stage_piece_p28.sh" "$SRC/replica234.py" "$RUN/instruments/"
"$PY" - "$TMPL" "$RUN/submit.sbatch" "$RUN" "$RUNID" "$SHA" "$WTIME" "$JOBNAME" "$TAG" "$T25" "$@" <<'PYEOF'
import pathlib, sys
tmpl, out, run, runid, sha, wtime, job, tag, t25 = sys.argv[1:10]
extra = dict(a.split("=", 1) for a in sys.argv[10:])
rep = {"__RUNDIR__": run, "__RUNID__": runid, "__NEWCOMMIT__": sha,
       "__IXTAG__": tag, "__JOBNAME__": job, "__TIME__": wtime,
       "__T25DUMP__": t25, "__PIECE__": "Pot_A_Piece_07", "__POT__": "Pot_A"}
if "__POTADUMP__" in pathlib.Path(tmpl).read_text():
    rep["__POTADUMP__"] = extra.get("POTADUMP", "")
t = pathlib.Path(tmpl).read_text()
for k, v in rep.items():
    t = t.replace(k, v)
left = sorted(set(p for p in rep if p in t))
if left:
    raise SystemExit("[SUBMIT] unfilled placeholders: %r" % left)
pathlib.Path(out).write_text(t)
print("[SUBMIT] wrote", out, len(t), "bytes")
PYEOF
if grep -lU $'\r' "$RUN/submit.sbatch" "$RUN/instruments"/*.sh "$RUN/instruments"/*.py 2>/dev/null; then
  echo "[SUBMIT] FATAL CRLF in submitted files"; exit 4
fi
echo "[SUBMIT] no CRLF; run=$RUNID sha=$SHA"
cd "$RUN" && sbatch submit.sbatch | tee logs/sbatch.txt
