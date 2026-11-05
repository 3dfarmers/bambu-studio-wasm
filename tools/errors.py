"""Summarise compiler/linker errors from a build log: file -> unique messages."""
import re
import sys
from collections import defaultdict

log = open(sys.argv[1], encoding="utf-8", errors="replace").read()
by_file = defaultdict(list)
for m in re.finditer(r"^(.*?):(\d+):\d+: (?:fatal )?error: (.*)$", log, flags=re.M):
    f = m.group(1).replace("\\", "/")
    f = re.sub(r"^.*?/bambu/", "", f)
    msg = f"{m.group(2)}: {m.group(3)}"
    if msg not in by_file[f]:
        by_file[f].append(msg)
for f, msgs in by_file.items():
    print(f"== {f} ({len(msgs)})")
    for msg in msgs[: int(sys.argv[2]) if len(sys.argv) > 2 else 15]:
        print("   " + msg[:190])
undef = sorted(set(re.findall(r"undefined symbol: (.*)", log)))
if undef:
    print(f"== undefined symbols ({len(undef)})")
    for u in undef:
        print("   " + u[:190])
