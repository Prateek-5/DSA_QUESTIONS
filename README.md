# DSA_QUESTIONS

A click-to-code DSA practice system. Open a problem from a visual **launchpad**, code it in
VS Code with the real description beside you, then **submit to LeetCode and push to GitHub in one
keystroke**.

226 problems in curated study order across 22 topics (sourced from the
[question-bank](https://github.com/Prateek-5/question-bank) learning path), with **real LeetCode
difficulties**.

## Quickstart (clone & go)

```bash
git clone <your-repo-ssh-url> DSA_QUESTIONS && cd DSA_QUESTIONS
bash tooling/install.sh                 # installs the VS Code extension + leetcode-cli
leetcode user -c                        # cookie login (see SETUP.md)
git remote set-url origin <your-repo>   # push to YOUR GitHub
code .                                  # open launchpad.html → click "Open ▸"
```
Shortcuts ship with the extension. Full details in **[SETUP.md](./SETUP.md)**.

## How it works

```
launchpad.html  ──click "Open"──►  vscode://prateek.dsa-bank/open?...
                                          │
                                   dsa-bank extension
                                          │  scaffolds + fetches description, marks "In Progress"
                                          ▼
        DSA/Solutions/<topic>/<NNN-slug>/{README.md, solution.cpp}
                                          │  you solve it
                                          ▼
            Ctrl+Alt+S → leetcode submit ─(Accepted)─► mark "Done" + git push
```

- **Open in VS Code** — `launchpad.html` has an *Open ▸* button per problem. Clicking it scaffolds
  `DSA/Solutions/<topic>/<NNN-slug>/` (LeetCode description → `README.md`, starter → `solution.cpp`),
  opens both side-by-side, and flips its status to **In Progress**. Existing problems just re-open.
- **Live status tracking** — each problem shows **To Do / In Progress / Done** in the launchpad, with
  a progress bar and a status filter. Status is stored in `data/status.json`, set automatically
  (Open → In Progress, Accepted submit → Done), and the page auto-refreshes to stay current.
- **Submit & Push** — one command submits to LeetCode (updates your profile) and, only if
  **Accepted**, marks Done, commits + pushes here. No redundant re-solve on the website.
- **Multiple approaches** — `Ctrl+Alt+N` spins up `approach-2.cpp`, `approach-3.cpp`… in the same
  folder; each is independently submittable and all coexist in GitHub (nothing overwritten).

## Keybindings (shipped with the extension)

| Key | Action |
|---|---|
| `Ctrl+Alt+R` | Test (LeetCode example cases, no submission) |
| `Ctrl+Alt+S` | Submit & Push (Accepted → Done + push) |
| `Ctrl+Alt+N` | New Approach (copy current solution) |

## Layout

| Path | What |
|---|---|
| `launchpad.html` | Clickable, filterable index of all 226 problems + live status |
| `data/problems.json` | Parsed metadata (source of truth for the launchpad/extension) |
| `data/status.json` | Per-problem status (`todo`/`open`/`done`) |
| `DSA/Solutions/…` | Your per-problem folders (created on demand) |
| `tooling/dsa-bank/` | The VS Code extension (TS source + packaged `.vsix`, ships keybindings) |
| `tooling/install.sh` | One-shot bootstrap for a fresh clone |
| `tooling/generate.py` | Rebuilds `problems.json` + `launchpad.html` |
| `tooling/set-status.py` | Updates `status.json` + re-renders the launchpad |
| `tooling/lc-submit.sh` | Submit-to-LeetCode + mark Done + push |
| `tooling/lc-test.sh` | Dry-run example cases (no submission) |
| `tooling/new-approach.sh` | Copy current solution → `approach-N.<ext>` |
| `.vscode/tasks.json` | DSA tasks (also runnable from the Command Palette) |

## Setup
See **[SETUP.md](./SETUP.md)** — install the extension, log in to `leetcode-cli` (cookie), bind a key.
