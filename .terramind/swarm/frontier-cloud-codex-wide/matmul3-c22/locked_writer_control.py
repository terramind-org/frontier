#!/usr/bin/env python3
"""Isolated crash/concurrency controls for the locked append-only writer."""
import argparse
import fcntl
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def atomic(path, value):
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    with os.fdopen(fd, "w") as out:
        out.write(json.dumps(value, sort_keys=True) + "\n")
        out.flush(); os.fsync(out.fileno())
    Path(tmp).replace(path)


def lock(records):
    handle = Path(str(records) + ".lock").open("a+")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handle.close()
        raise RuntimeError("writer already owns stream lock")
    return handle


def write(records, cursor, stop=None):
    holder = lock(records)
    try:
        done = [] if not records.exists() else [json.loads(x) for x in records.read_text().splitlines()]
        for expected, row in enumerate(done):
            if row != {"order_index": expected, "token": f"synthetic-{expected}"}:
                raise ValueError("bad durable stream")
        for index in range(len(done), 12):
            with records.open("a") as out:
                out.write(json.dumps({"order_index": index, "token": f"synthetic-{index}"}, sort_keys=True) + "\n")
                out.flush(); os.fsync(out.fileno())
            if stop == index:
                return "interrupted-after-append"
            atomic(cursor, {"next_order_index": index + 1})
        return "complete"
    finally:
        holder.close()


def child(records):
    holder = lock(Path(records))
    try:
        print("locked", flush=True)
        import time; time.sleep(1)
    finally:
        holder.close()


def main():
    root = Path(__file__).with_name("writer-control-fixture")
    root.mkdir(exist_ok=True)
    for name in ("uninterrupted.jsonl", "resumed.jsonl", "checkpoint.json", "resumed-checkpoint.json"):
        (root / name).unlink(missing_ok=True)
    uninterrupted = root / "uninterrupted.jsonl"
    resumed = root / "resumed.jsonl"
    assert write(uninterrupted, root / "checkpoint.json") == "complete"
    assert write(resumed, root / "resumed-checkpoint.json", stop=4) == "interrupted-after-append"
    # The row exists durably while the cursor is deliberately stale; recovery
    # derives the next row from records, not the stale cursor.
    assert write(resumed, root / "resumed-checkpoint.json") == "complete"
    assert uninterrupted.read_bytes() == resumed.read_bytes()
    proc = subprocess.Popen([sys.executable, __file__, "--child", str(root / "concurrent.jsonl")], stdout=subprocess.PIPE, text=True)
    assert proc.stdout.readline().strip() == "locked"
    rejected = False
    try:
        write(root / "concurrent.jsonl", root / "concurrent-checkpoint.json")
    except RuntimeError:
        rejected = True
    assert rejected and not (root / "concurrent.jsonl").exists()
    assert proc.wait() == 0
    report = {"concurrent_second_writer_rejected_before_write": True,
              "interrupt_after_append_recovered": True,
              "resumed_bytes_equal_uninterrupted": True,
              "rows": 12}
    atomic(root / "report.json", report)
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--child", action="store_true"); parser.add_argument("records", nargs="?")
    args = parser.parse_args()
    if args.child: child(args.records)
    else: main()
