#!/usr/bin/env bash
# check-stage55.sh -- laptop-side gates over the stage55 instruments, before commit.
# Exit 0 = safe to commit.  Run from anywhere; takes the instruments dir as $1 (default:
# the directory of this script).
set -euo pipefail
D="${1:-$(cd "$(dirname "$0")" && pwd)}"
cd "$D"
fail=0
ok()   { echo "  ok   $*"; }
bad()  { echo "  FAIL $*"; fail=1; }

echo "[C55] instruments in $D"
for f in run_cell55.sh render55.py submit55.sh submit55.sbatch.tmpl stage_synth_p40.sh .gitattributes; do
  [ -f "$f" ] && ok "present $f" || bad "missing $f"
done

# LF only, everywhere (the t54 CRLF trap)
for f in *.sh *.py *.tmpl .gitattributes; do
  if grep -qU $'\r' "$f"; then bad "CRLF in $f"; else ok "LF $f"; fi
done

# syntax
bash -n run_cell55.sh      && ok "bash -n run_cell55.sh"      || bad "bash -n run_cell55.sh"
bash -n submit55.sh        && ok "bash -n submit55.sh"        || bad "bash -n submit55.sh"
bash -n stage_synth_p40.sh && ok "bash -n stage_synth_p40.sh" || bad "bash -n stage_synth_p40.sh"
python -m py_compile render55.py && ok "py_compile render55.py" || bad "py_compile render55.py"

# the fact table: header must carry exactly 12 columns (11 tab separators), the width
# every row enforces; the header line is the one that opens pieces55.tsv
NS=$(grep -m1 '^printf "piece' run_cell55.sh | grep -o '\\t' | wc -l || true)
[ "$NS" -eq 11 ] && ok "fact table header 12 cols (11 tabs)" || bad "fact table header has $NS tabs (want 11)"

# template: every placeholder known and present, nothing unknown left to chance
for ph in __JOBNAME__ __RUNID__ __RUNDIR__ __NEWCOMMIT__ __IXTAG__ __TIME__; do
  n=$(grep -o "$ph" submit55.sbatch.tmpl | wc -l)
  [ "$n" -ge 1 ] && ok "placeholder $ph x$n" || bad "placeholder $ph missing"
done
UNK=$(grep -oE '__[A-Z0-9]+__' submit55.sbatch.tmpl | sort -u | grep -vE '^__(JOBNAME|RUNID|RUNDIR|NEWCOMMIT|IXTAG|TIME)__$' | wc -l || true)
[ "$UNK" -eq 0 ] && ok "no unknown placeholders" || bad "unknown placeholder in submit55.sbatch.tmpl"

# the tmpl must still be the one that defends the paid-for traps
NUN=$(grep -o 'SFS_' submit55.sbatch.tmpl | wc -l)
[ "$NUN" -ge 20 ] && ok "tmpl unsets/touches $NUN SFS_ refs" || bad "tmpl only $NUN SFS_ refs (unset list lost?)"
grep -q 'grep -a' run_cell55.sh && ok "binary grep -a present" || bad "no grep -a in run_cell55.sh"
grep -q 'xargs -0\|xargs -d' submit55.sbatch.tmpl && ok "safe xargs mode" || bad "check xargs delimiter use"

# .gitattributes keeps the whole tree LF for git archive
grep -q '^\* -text' .gitattributes && ok "gitattributes '* -text'" || bad ".gitattributes not '* -text'"

[ "$fail" -eq 0 ] && echo "[C55] ALL GATES PASS" || { echo "[C55] GATES FAILED"; exit 1; }
