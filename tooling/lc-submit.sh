#!/usr/bin/env bash
# Submit a solution to LeetCode and, if Accepted, commit + push to GitHub.
# Usage:  bash tooling/lc-submit.sh <path/to/solution.cpp>
# GeeksforGeeks / non-LeetCode problems skip submission and just push.
set -uo pipefail

FILE="${1:-}"
if [[ -z "$FILE" || ! -f "$FILE" ]]; then
  echo "✘ usage: lc-submit.sh <solution-file>"; exit 1
fi
FILE="$(realpath "$FILE")"
FOLDER="$(dirname "$FILE")"
NAME="$(basename "$FOLDER")"
FNAME="$(basename "$FILE")"          # e.g. solution.cpp or approach-2.cpp
ID="${NAME%%-*}"                     # e.g. 001
ROOT="$(git -C "$FOLDER" rev-parse --show-toplevel 2>/dev/null)"
if [[ -z "$ROOT" ]]; then echo "✘ not inside a git repo"; exit 1; fi

bold(){ printf "\033[1m%s\033[0m\n" "$1"; }
green(){ printf "\033[32m%s\033[0m\n" "$1"; }
red(){ printf "\033[31m%s\033[0m\n" "$1"; }

mark_done(){ # update launchpad status (best-effort)
  python3 "$ROOT/tooling/set-status.py" "$ID" done >/dev/null 2>&1 || true
}

commit_push(){ # $1 = commit message
  ( cd "$ROOT"
    git add "$FOLDER" "$ROOT/data/status.json" "$ROOT/launchpad.html" 2>/dev/null || git add "$FOLDER"
    if git diff --cached --quiet; then
      echo "• nothing new to commit";
    else
      git commit -q -m "$1" && green "✔ committed: $1"
    fi
    bold "→ pushing to origin/main…"
    if git push -q origin HEAD:main; then green "✔ pushed to GitHub"; else red "✘ push failed (check: ssh -T git@github-personal)"; exit 1; fi
  )
}

# --- LeetCode problem? (has the @lc header) ---
if grep -q "@lc app=leetcode" "$FILE"; then
  if ! command -v leetcode >/dev/null 2>&1; then
    red "✘ leetcode-cli not found."
    echo "  install:  npm i -g vsc-leetcode-cli"
    echo "  then log in (see SETUP.md):  leetcode plugin -i cookie && leetcode user -c"
    exit 1
  fi
  bold "→ submitting $NAME to LeetCode…"
  LOG="$(leetcode submit "$FILE" 2>&1)"
  echo "$LOG"
  if echo "$LOG" | grep -qiE "accepted|✔ .* cases passed"; then
    green "✔ Accepted on LeetCode (profile updated)"
    mark_done
    RUNTIME="$(echo "$LOG" | grep -oiE "[0-9]+ ms" | head -1)"
    commit_push "solve: ${NAME}/${FNAME} [Accepted${RUNTIME:+, $RUNTIME}]"
  elif echo "$LOG" | grep -qiE "code=(499|403|401)|session expired|please ?login|not ?login|login first"; then
      red "✘ LeetCode session expired or invalid — this is NOT a code problem."
      echo "  Re-login, then resubmit:  leetcode user -c"
      echo "  (paste:  csrftoken=<CSRF>; LEETCODE_SESSION=<SESSION>  from leetcode.com → F12 → Cookies)"
      exit 2
    else
      red "✘ Not accepted (Wrong Answer / TLE / Runtime / Compile) — NOT pushing. Fix and re-run."
      echo "  (tip: dry-run first — 'leetcode test \"$FILE\"' or Ctrl+Alt+R)"
      exit 1
    fi
else
  bold "→ non-LeetCode problem (GeeksforGeeks/misc): skipping submit, pushing solution."
  mark_done
  commit_push "solve: ${NAME}/${FNAME}"
fi
