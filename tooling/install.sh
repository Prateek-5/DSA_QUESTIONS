#!/usr/bin/env bash
# One-shot bootstrap for a fresh clone of DSA_QUESTIONS.
# Installs the VS Code extension + leetcode-cli, then prints the 2 manual steps.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
green(){ printf "\033[32m%s\033[0m\n" "$1"; }
warn(){ printf "\033[33m%s\033[0m\n" "$1"; }

echo "── DSA_QUESTIONS bootstrap ──"

# 1) VS Code extension (ships keybindings: Ctrl+Alt+S / R / N)
if command -v code >/dev/null 2>&1; then
  code --install-extension "$ROOT/tooling/dsa-bank/dsa-bank.vsix" --force && green "✔ dsa-bank extension installed"
else
  warn "! 'code' CLI not found. Install VS Code, then run:"
  warn "    code --install-extension tooling/dsa-bank/dsa-bank.vsix"
fi

# 2) leetcode-cli (for submit/test)
if command -v leetcode >/dev/null 2>&1; then
  green "✔ leetcode-cli already installed"
elif command -v npm >/dev/null 2>&1; then
  echo "→ installing leetcode-cli (vsc-leetcode-cli)…"
  npm i -g vsc-leetcode-cli && green "✔ leetcode-cli installed" || warn "! npm install failed; run: npm i -g vsc-leetcode-cli"
else
  warn "! npm not found. Install Node.js, then: npm i -g vsc-leetcode-cli"
fi

# 3) make sure launchpad/status exist
[ -f "$ROOT/data/status.json" ] || python3 "$ROOT/tooling/generate.py" >/dev/null 2>&1 || true

cat <<EOF

── Two manual steps left ──
  1) Log in to LeetCode (cookie):
       leetcode user -c
     login:  <your LeetCode username>
     cookie: csrftoken=<CSRF>; LEETCODE_SESSION=<SESSION>   (from leetcode.com → F12 → Application → Cookies)

  2) Point this repo at YOUR GitHub remote (a clone points at the original):
       git remote set-url origin <your-repo-ssh-url>
       git config user.name  "Your Name"
       git config user.email "you@example.com"

Then:  code "$ROOT"   → open launchpad.html → click Open ▸ on a problem.
Shortcuts ship with the extension:  Ctrl+Alt+S submit · Ctrl+Alt+R test · Ctrl+Alt+N new approach
EOF
green "Bootstrap done."
