#!/usr/bin/env python3
import os
import signal
import sys
import time

ORDER = [
    "Hierarchy-E_K1R2",
    "Hierarchy-E_MOR1",
    "Hierarchy-E_BASER2",
    "Hierarchy-E_MOR2",
    "Hierarchy-E_K1R1",
    "Hierarchy-E_BASER1",
    "Hierarchy-E_K6R1",
    "Hierarchy-E_K6R2",
    "Hierarchy-E_K2R2",
    "Hierarchy-E_K2R1",
    "Hierarchy-E_K3R1",
    "Hierarchy-E_K3R2",
]
MAX_ACTIVE = 4


def get_hierarchy_procs():
    my_pid = os.getpid()
    found = {}
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        pid = int(entry)
        if pid == my_pid:
            continue
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as f:
                raw = f.read().split(b"\x00")
            if not raw or not raw[0]:
                continue
            arg0 = os.path.basename(raw[0].decode("utf-8", errors="ignore"))
            if arg0.startswith("Hierarchy-E_"):
                found[arg0] = pid
        except Exception:
            continue
    return found


def pin_proc_threads(pid, cpu_set):
    if not cpu_set:
        return
    try:
        task_dir = f"/proc/{pid}/task"
        for tid_s in os.listdir(task_dir):
            if tid_s.isdigit():
                try:
                    os.sched_setaffinity(int(tid_s), cpu_set)
                except Exception:
                    pass
    except Exception:
        pass


def step_once(all_cpus, prev_active):
    found = get_hierarchy_procs()
    if not found:
        return False, set()
    active_list = []
    for name in ORDER:
        if name not in found:
            continue
        pid = found[name]
        if len(active_list) < MAX_ACTIVE:
            slot = len(active_list)
            chunk = len(all_cpus) // MAX_ACTIVE
            slot_cpus = set(all_cpus[slot * chunk : (slot + 1) * chunk]) if chunk > 0 else set(all_cpus)
            pin_proc_threads(pid, slot_cpus)
            try:
                os.kill(pid, signal.SIGCONT)
            except Exception:
                pass
            active_list.append((name, pid, sorted(slot_cpus)))
        else:
            try:
                os.kill(pid, signal.SIGSTOP)
            except Exception:
                pass
    cur_active = {name for name, _, _ in active_list}
    if cur_active != prev_active:
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        act_str = ", ".join(f"{n}(pid={p},cpus={c[0]}..{c[-1]})" for n, p, c in active_list)
        print(f"[throttle {ts}] active={len(active_list)}/{len(found)}: {act_str}", flush=True)
    return True, cur_active


def main():
    daemon = "--daemon" in sys.argv
    try:
        all_cpus = sorted(os.sched_getaffinity(0))
    except Exception:
        all_cpus = []
    prev_active = set()
    if not daemon:
        step_once(all_cpus, prev_active)
        return 0
    while True:
        alive, prev_active = step_once(all_cpus, prev_active)
        if not alive:
            print("[throttle] all Hierarchy-E_* processes finished.", flush=True)
            return 0
        time.sleep(5)


if __name__ == "__main__":
    sys.exit(main())
