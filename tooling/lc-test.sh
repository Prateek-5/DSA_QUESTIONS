#!/usr/bin/env bash
# Dry-run a solution against LeetCode's example cases. No submission, no push,
# no effect on your submission history.
# Usage:  bash tooling/lc-test.sh <path/to/solution.cpp>
set -uo pipefail

FILE="${1:-}"
if [[ -z "$FILE" || ! -f "$FILE" ]]; then
  echo "✘ usage: lc-test.sh <solution-file>"; exit 1
fi
FILE="$(realpath "$FILE")"
NAME="$(basename "$(dirname "$FILE")")"

if ! grep -q "@lc app=leetcode" "$FILE"; then
  echo "• $NAME is not a LeetCode problem (no @lc header) — nothing to test."
  exit 0
fi
if ! command -v leetcode >/dev/null 2>&1; then
  echo "✘ leetcode-cli not found. install: npm i -g vsc-leetcode-cli"; exit 1
fi

printf "\033[1m→ testing %s against LeetCode example cases (no submission)…\033[0m\n" "$NAME"
leetcode test "$FILE"
