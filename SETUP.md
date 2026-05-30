# Setup

## Quickstart (cloning this repo)

```bash
git clone <your-fork-ssh-url> DSA_QUESTIONS
cd DSA_QUESTIONS
bash tooling/install.sh        # installs the VS Code extension + leetcode-cli
leetcode user -c               # log in (see step 3 below)
git remote set-url origin <your-repo>   # push to YOUR GitHub, not the original
code .                         # open the repo, then open launchpad.html
```
The keybindings (`Ctrl+Alt+S` / `R` / `N`) **ship with the extension** — nothing to configure.

---

## Manual reference

### 1. Install the `dsa-bank` VS Code extension
```bash
code --install-extension tooling/dsa-bank/dsa-bank.vsix --force
```
Installing it also registers the shortcuts below. Reload VS Code after install.

### 2. Always open the repo as the workspace
The extension scaffolds into the **first workspace folder**:
```bash
code /path/to/DSA_QUESTIONS
```

### 3. Install + log in to leetcode-cli (needed for Test / Submit)
```bash
npm i -g vsc-leetcode-cli      # provides the `leetcode` command
leetcode user -c               # cookie login (do NOT run `plugin -i cookie` — its URL is dead/404)
```
`leetcode user -c` prompts for two things:
- **login** → your LeetCode username
- **cookie** → one line with **both** values: `csrftoken=<CSRF>; LEETCODE_SESSION=<SESSION>`

Get them at leetcode.com → **F12 → Application → Cookies → `https://leetcode.com`** → copy the
`csrftoken` and `LEETCODE_SESSION` values. Verify with `leetcode user`. (Cookie expires every few
weeks — just re-run `leetcode user -c`. The `padLevels` warning is harmless.)

### 4. Point the repo at your own GitHub
A clone's `origin` is the original repo. To push your solutions to your own:
```bash
git remote set-url origin <your-repo-ssh-url>
git config user.name "Your Name"; git config user.email "you@example.com"
```

---

## Keybindings (shipped by the extension)

| Key | Command | Effect |
|---|---|---|
| `Ctrl+Alt+R` | DSA: Test | `leetcode test` — example cases only, no submission |
| `Ctrl+Alt+S` | DSA: Submit & Push | Submit → if **Accepted**, mark Done + commit + push |
| `Ctrl+Alt+N` | DSA: New Approach | Copy the open file → `approach-N.cpp` and open it |

> On GNOME, `Ctrl+Alt+T` is reserved by the OS (opens a terminal) — that's why **Test is `Ctrl+Alt+R`**.
> All three are also in the Command Palette under **DSA:**. To rebind, use VS Code's Keyboard Shortcuts UI.

---

## Daily workflow

1. Open **`launchpad.html`** (double-click, or Command Palette → **DSA: Open Launchpad**).
2. Click **Open ▸** → scaffolds + opens the problem; its status auto-flips to **In Progress**.
3. Solve. `Ctrl+Alt+R` to dry-run the examples.
4. `Ctrl+Alt+S` → submits to LeetCode; if **Accepted**, status auto-flips to **Done** and the
   solution + status are committed and pushed.
5. Want another approach? `Ctrl+Alt+N` → a fresh `approach-N.cpp` to edit; submit it the same way.

Status (To Do / In Progress / Done) is stored in `data/status.json` and embedded into
`launchpad.html`; the launchpad auto-refreshes every few seconds so it stays current (toggle with the
**auto-refresh** checkbox).

---

## Maintenance

Re-render the launchpad (clone-friendly, uses committed `data/problems.json`):
```bash
python3 tooling/generate.py
```
Full rebuild from the source question-bank:
```bash
QB=/path/to/question-bank DIFF_JSON=/path/to/leet_diff.json python3 tooling/generate.py
```
Re-package the extension after editing it:
```bash
cd tooling/dsa-bank && npm install && npm run compile && npm run package
code --install-extension dsa-bank.vsix --force
```
