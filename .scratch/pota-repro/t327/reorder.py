p = ".scratch/pota-repro/issues/327-juglet-wall-side-cause.md"
s = open(p, encoding="utf-8").read()
i5 = s.index("### Bar 5")
i4b = s.index("### Bar 4b")
iv = s.index("### Verdicts, and what is left to the fix")
assert i5 < i4b < iv
head, sec5, sec4b, tail = s[:i5], s[i5:i4b], s[i4b:iv], s[iv:]
s2 = head + sec4b + sec5 + tail
open(p, "w", encoding="utf-8", newline="\n").write(s2)
import re
print([m for m in re.findall(r"^### .*$", s2, re.M)])
