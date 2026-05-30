#!/usr/bin/env python3
"""Set a problem's status and re-render launchpad.html.

Usage:  python3 tooling/set-status.py <id> <todo|open|done>
- 'done' is sticky: an 'open' will not downgrade a problem already 'done'.
"""
import sys, os, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate  # noqa: E402

VALID = {"todo", "open", "done"}


def main():
    if len(sys.argv) != 3 or sys.argv[2] not in VALID:
        print("usage: set-status.py <id> <todo|open|done>")
        sys.exit(1)
    pid, new = sys.argv[1], sys.argv[2]
    rows = generate.load_problems()
    status = generate.load_status(rows)
    if not any(r["id"] == pid for r in rows):
        print(f"unknown id {pid}")
        sys.exit(1)
    if not (status.get(pid) == "done" and new == "open"):  # don't downgrade done->open
        status[pid] = new
    generate.save_status(status)
    generate.render_launchpad(rows, status)
    print(f"status[{pid}] = {status[pid]}; launchpad re-rendered")


if __name__ == "__main__":
    main()
