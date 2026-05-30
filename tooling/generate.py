#!/usr/bin/env python3
"""Generate data/problems.json and launchpad.html.

Two modes:
  - Full build (needs the source question-bank):  QB=/path/to/question-bank python3 tooling/generate.py
  - Re-render only (clone-friendly, uses committed data/problems.json):  python3 tooling/generate.py

Status lives in data/status.json (id -> "todo" | "open" | "done") and is embedded into
launchpad.html on every render. set-status.py updates it; this module re-renders.
"""
import re, os, json, html, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
QB = os.environ.get("QB", "")
DIFF_JSON = os.environ.get("DIFF_JSON", "/tmp/leet_diff.json")
EXT_ID = "prateek.dsa-bank"
PROBLEMS = os.path.join(ROOT, "data", "problems.json")
STATUS = os.path.join(ROOT, "data", "status.json")

STAGE_ORDER = [
    ("Arrays_and_Matrices", 1), ("1_D_and_2_D_Arrays", 1), ("Two_Pointers", 1),
    ("Hashing_Sliding_Window", 1), ("Stack", 1), ("Linked_List", 1), ("Searching_Binary_Search", 1),
    ("Math", 2), ("Bit_Manipulation", 2), ("Queues_Deque_Monotonic_Queue", 2),
    ("Sorting_Divide_and_Conquer", 2), ("Recursion", 2), ("Backtracking", 2),
    ("Trees_Binary_Trees", 3), ("Binary_Search_Tree_BST", 3), ("Trie_Bit_Manipulation_Trie", 3),
    ("Heap_Priority_Queue", 3), ("Graph_BFS_DFS_Dijkstra_DSU", 3),
    ("Greedy", 4), ("Dynamic_Programming_DP", 4), ("Segment_Tree_Range_Queries", 4),
    ("Number_Theory_Misc", 4),
]
STAGE_NAME = {1: "1 · Foundations", 2: "2 · Structures & Idioms",
              3: "3 · Trees & Graphs", 4: "4 · Optimization & Advanced"}
TOPIC_DISPLAY = {
    "Arrays_and_Matrices": "Arrays & Matrices", "1_D_and_2_D_Arrays": "1D & 2D Arrays (Prefix Sums)",
    "Two_Pointers": "Two Pointers", "Hashing_Sliding_Window": "Hashing & Sliding Window",
    "Stack": "Stack", "Linked_List": "Linked List", "Searching_Binary_Search": "Binary Search",
    "Math": "Math", "Bit_Manipulation": "Bit Manipulation",
    "Queues_Deque_Monotonic_Queue": "Queues / Monotonic Deque",
    "Sorting_Divide_and_Conquer": "Sorting & Divide and Conquer", "Recursion": "Recursion",
    "Backtracking": "Backtracking", "Trees_Binary_Trees": "Trees / Binary Trees",
    "Binary_Search_Tree_BST": "Binary Search Tree (BST)", "Trie_Bit_Manipulation_Trie": "Trie",
    "Heap_Priority_Queue": "Heap / Priority Queue",
    "Graph_BFS_DFS_Dijkstra_DSU": "Graphs (BFS/DFS/Dijkstra/DSU)", "Greedy": "Greedy",
    "Dynamic_Programming_DP": "Dynamic Programming", "Segment_Tree_Range_Queries": "Segment Tree / Range Queries",
    "Number_Theory_Misc": "Number Theory & Misc",
}
BLOB = "https://github.com/Prateek-5/question-bank/blob/main/DSA/Topics"
ITEM = re.compile(r'^\s*\d+\.\s+\*\*\[(?P<file>[^\]]+\.md)\]')
WALK = re.compile(r'\(\.?/?learn/[^)]+\)')

LEET_DIFF = {}
if os.path.exists(DIFF_JSON):
    LEET_DIFF = {k: v for k, v in json.load(open(DIFF_JSON)).items() if v}


def leetcode_link(qp):
    try:
        txt = open(qp).read()
    except OSError:
        return ""
    m = re.search(r'Problem Link:\*?\*?\s*\n+\s*(\S+)', txt)
    return m.group(1) if m else ""


def slug_of(url):
    m = re.search(r'leetcode\.com/problems/([^/?#]+)', url or "")
    return m.group(1) if m else None


def slugify(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def classify(stage, mustdo, desc):
    d = desc.lower()
    hard = ["senior signal", "the classic", "all-time classic", "hardest", "trickiest",
            "lazy propagation", "hard", "dijkstra", "advanced", "two-heap", "digit dp",
            "monotonic stack", "kahn", "tarjan", "bellman"]
    easy = ["warm-up", "warm up", "hello-world", "hello world", "basic", "cleanest", "simplest"]
    if any(k in d for k in hard): return "Hard"
    if any(k in d for k in easy): return "Easy"
    if stage == 1: return "Easy" if not mustdo else "Medium"
    if stage == 4: return "Hard" if mustdo else "Medium"
    return "Medium"


def parse():
    rows, g = [], 0
    for tdir, stage in STAGE_ORDER:
        lp = os.path.join(QB, "DSA/Topics", tdir, "LEARNING.md")
        if not os.path.exists(lp):
            sys.exit(f"missing {lp}; set QB=/path/to/question-bank")
        pattern, tidx = "", 0
        for line in open(lp):
            h = re.match(r'^###\s+(.*)', line)
            if h:
                pattern = re.sub(r'\s+[—–-]\s+.*$', '', h.group(1)).strip()
                continue
            m = ITEM.match(line)
            if not m:
                continue
            g += 1; tidx += 1
            fname = m.group("file")
            rest = line[m.end():]
            mustdo = "must-do" in rest.lower()
            rc = WALK.sub('', rest)
            rc = re.sub(r'\[walkthrough[^\]]*\]', '', rc)
            dm = re.search(r'[—-]\s*(.+)$', rc)
            desc = (dm.group(1) if dm else "").replace("**must-do**", "").replace("must-do", "")
            desc = re.sub(r'\s*·\s*$', '', desc).strip(" .·*").strip()
            title = fname[:-3].replace("_", " ")
            qpath = os.path.join(QB, "DSA/Topics", tdir, fname)
            leet = leetcode_link(qpath)
            lslug = slug_of(leet)
            kind = "leetcode" if lslug else ("gfg" if "geeksforgeeks" in (leet or "") else "other")
            real = LEET_DIFF.get(lslug or "")
            diff, est = (real, False) if real else (classify(stage, mustdo, desc), True)
            fslug = lslug or slugify(fname[:-3])
            rows.append(dict(
                order=g, id=f"{g:03d}", stage=stage, stageName=STAGE_NAME[stage],
                topicDir=tdir, topic=TOPIC_DISPLAY[tdir], topicIndex=tidx, pattern=pattern,
                title=title, fileSlug=fslug, leetSlug=lslug or "", kind=kind,
                ref=f"{BLOB}/{tdir}/{fname}",
                walk=(f"{BLOB}/{tdir}/learn/{fname}"
                      if os.path.exists(os.path.join(QB, "DSA/Topics", tdir, "learn", fname)) else ""),
                leet=leet, priority=("Must-Do" if mustdo else "Optional"),
                difficulty=diff, difficultyEst=est, desc=desc,
                folder=f"DSA/Solutions/{tdir}/{g:03d}-{fslug}",
            ))
    return rows


def load_problems():
    """Parse from QB if available (full build), else load committed problems.json."""
    if QB and os.path.isdir(QB):
        rows = parse()
        os.makedirs(os.path.dirname(PROBLEMS), exist_ok=True)
        json.dump(rows, open(PROBLEMS, "w"), indent=2)
        return rows
    if os.path.exists(PROBLEMS):
        return json.load(open(PROBLEMS))
    sys.exit("No data/problems.json and QB not set. Run once with QB=/path/to/question-bank.")


def load_status(rows):
    st = {}
    if os.path.exists(STATUS):
        try:
            st = json.load(open(STATUS))
        except Exception:
            st = {}
    for r in rows:
        st.setdefault(r["id"], "todo")
    return st


def save_status(st):
    os.makedirs(os.path.dirname(STATUS), exist_ok=True)
    json.dump(st, open(STATUS, "w"), indent=0)


# ---------------- launchpad.html ----------------
STAGE_BAR = {1: "#1565C0", 2: "#2E7D32", 3: "#EF6C00", 4: "#6A1B9A"}
STAGE_TINT = {1: "#E3F2FD", 2: "#E8F5E9", 3: "#FFF3E0", 4: "#F3E5F5"}
DIFF_COLOR = {"Easy": "#2E7D32", "Medium": "#E65100", "Hard": "#B71C1C"}
STATUS_META = {  # key -> (label, text-color, bg)
    "todo": ("To Do", "#64748B", "#EEF2F5"),
    "open": ("In Progress", "#E65100", "#FFF3E0"),
    "done": ("Done", "#2E7D32", "#E8F5E9"),
}


def vscode_uri(r):
    from urllib.parse import urlencode
    q = urlencode({"id": r["id"], "topic": r["topicDir"], "slug": r["fileSlug"],
                   "title": r["title"], "leetslug": r["leetSlug"], "kind": r["kind"],
                   "src": r["leet"] or r["ref"], "ref": r["ref"]})
    return f"vscode://{EXT_ID}/open?{q}"


def render_launchpad(rows, status):
    n = len(rows)
    must = sum(1 for r in rows if r["priority"] == "Must-Do")
    done = sum(1 for r in rows if status.get(r["id"]) == "done")
    parts = []
    parts.append(f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DSA Launchpad</title>
<style>
:root{{--ink:#1F2933;--mut:#627D88;--line:#E2E8F0;}}
*{{box-sizing:border-box}}
body{{font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;margin:0;color:var(--ink);background:#F8FAFC}}
header{{background:#0B3D5C;color:#fff;padding:18px 24px}}
header h1{{margin:0;font-size:20px}} header p{{margin:6px 0 0;opacity:.85;font-size:13px}}
.bar{{display:flex;gap:10px;flex-wrap:wrap;padding:14px 24px;background:#DCEBF7;position:sticky;top:0;z-index:5;border-bottom:1px solid var(--line);align-items:center}}
.bar input,.bar select{{padding:7px 10px;border:1px solid #B9CBD8;border-radius:8px;font-size:13px}}
.bar input{{flex:1;min-width:200px}}
.stat{{font-size:13px;color:#0B3D5C;font-weight:600}}
label.auto{{font-size:12px;color:#0B3D5C;display:flex;gap:5px;align-items:center}}
.prog{{height:8px;background:#cfe0ee;border-radius:6px;overflow:hidden;width:160px}}
.prog>i{{display:block;height:100%;background:#2E7D32}}
table{{border-collapse:collapse;width:100%;font-size:13px}}
th{{background:#0B3D5C;color:#fff;padding:9px 8px;text-align:left;position:sticky;top:60px;z-index:4}}
td{{padding:7px 8px;border-bottom:1px solid var(--line);vertical-align:top}}
tr:hover td{{background:#F1F7FC}}
.stage{{font-weight:700;white-space:nowrap}} .topic{{font-weight:600}}
.pat{{color:var(--mut);font-style:italic;font-size:12px}}
.desc{{color:var(--mut);font-size:12px;max-width:320px}}
.pill,.sbadge{{display:inline-block;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:700;white-space:nowrap}}
.must{{background:#FDE8E8;color:#B71C1C}} .opt{{background:#EEF2F5;color:#627D88}}
.diff{{font-weight:700}}
a.btn{{display:inline-block;padding:5px 10px;border-radius:7px;text-decoration:none;font-weight:600;font-size:12px;white-space:nowrap}}
a.open{{background:#0B3D5C;color:#fff}} a.open:hover{{background:#0a3350}}
a.lc{{color:#1565C0}} a.card{{color:#627D88}}
.est{{font-size:10px;color:#94A3B8}}
tr[data-status="done"] td:nth-child(n+3):nth-child(-n+6){{opacity:.6}}
.hide{{display:none}}
</style></head><body>
<header><h1>🚀 DSA Launchpad — {n} problems</h1>
<p>Click <b>Open</b> → scaffolds &amp; opens in VS Code (auto-marks <b>In Progress</b>). Submitting an
Accepted solution auto-marks <b>Done</b>. {must} must-do. Open the <code>DSA_QUESTIONS</code> repo in
VS Code with the <b>dsa-bank</b> extension installed.</p></header>
<div class="bar">
  <input id="q" placeholder="🔍 filter by title / topic / pattern…" oninput="flt()">
  <select id="st" onchange="flt()"><option value="">All stages</option>
    <option>1 · Foundations</option><option>2 · Structures &amp; Idioms</option>
    <option>3 · Trees &amp; Graphs</option><option>4 · Optimization &amp; Advanced</option></select>
  <select id="df" onchange="flt()"><option value="">All difficulty</option>
    <option>Easy</option><option>Medium</option><option>Hard</option></select>
  <select id="pr" onchange="flt()"><option value="">Any priority</option>
    <option>Must-Do</option><option>Optional</option></select>
  <select id="sf" onchange="flt()"><option value="">Any status</option>
    <option value="todo">To Do</option><option value="open">In Progress</option><option value="done">Done</option></select>
  <span class="stat" id="cnt"></span>
  <div class="prog" title="solved"><i id="bar" style="width:{(done*100//n) if n else 0}%"></i></div>
  <span class="stat" id="done"></span>
  <label class="auto"><input type="checkbox" id="auto" checked> auto-refresh</label>
  <button onclick="location.reload()" title="refresh now" style="border:1px solid #B9CBD8;border-radius:8px;background:#fff;cursor:pointer;padding:6px 9px">↻</button>
</div>
<table id="t"><thead><tr>
<th>#</th><th>Status</th><th>Stage</th><th>Topic</th><th>Pattern</th><th>Problem</th>
<th>Difficulty</th><th>Priority</th><th>Open</th><th>Links</th><th>Notes</th>
</tr></thead><tbody>""")
    for r in rows:
        dc = DIFF_COLOR[r["difficulty"]]
        est = '<span class="est">*</span>' if r["difficultyEst"] else ""
        prc = "must" if r["priority"] == "Must-Do" else "opt"
        emb = status.get(r["id"], "todo")
        smeta = STATUS_META[emb]
        lc = (f'<a class="btn lc" href="{html.escape(r["leet"])}" target="_blank">LeetCode↗</a>'
              if r["kind"] == "leetcode" else
              (f'<a class="btn lc" href="{html.escape(r["leet"])}" target="_blank">GfG↗</a>'
               if r["leet"] else ""))
        card = f'<a class="btn card" href="{html.escape(r["ref"])}" target="_blank">card↗</a>'
        blob = " ".join(filter(None, [r["title"].lower(), r["topic"].lower(), r["pattern"].lower(),
                                      r["difficulty"].lower(), r["priority"].lower(), r["stageName"].lower()]))
        parts.append(f"""<tr data-id="{r['id']}" data-emb="{emb}" data-status="{emb}" data-s="{html.escape(r['stageName'])}" data-d="{r['difficulty']}" data-p="{r['priority']}" data-b="{html.escape(blob)}">
<td>{r['order']}</td>
<td><span class="sbadge" style="color:{smeta[1]};background:{smeta[2]}">{smeta[0]}</span></td>
<td class="stage" style="color:{STAGE_BAR[r['stage']]}">{html.escape(r['stageName'])}</td>
<td class="topic">{html.escape(r['topic'])}</td>
<td class="pat">{html.escape(r['pattern'])}</td>
<td><b>{html.escape(r['title'])}</b></td>
<td class="diff" style="color:{dc}">{r['difficulty']}{est}</td>
<td><span class="pill {prc}">{r['priority']}</span></td>
<td><a class="btn open" href="{html.escape(vscode_uri(r))}" onclick="markOpen('{r['id']}')">Open ▸</a></td>
<td>{lc} {card}</td>
<td class="desc">{html.escape(r['desc'])}</td>
</tr>""")
    parts.append("""</tbody></table>
<script>
const META={todo:["To Do","#64748B","#EEF2F5"],open:["In Progress","#E65100","#FFF3E0"],done:["Done","#2E7D32","#E8F5E9"]};
const SKEY='dsa-status', FKEY='dsa-filters';
function lsGet(){try{return JSON.parse(localStorage.getItem(SKEY)||'{}')}catch(e){return {}}}
function lsSet(o){localStorage.setItem(SKEY,JSON.stringify(o))}
function eff(tr,ls){const id=tr.dataset.id,emb=tr.dataset.emb||'todo';
  if(emb==='done'||ls[id]==='done')return 'done'; return ls[id]||emb;}
function applyStatuses(){const ls=lsGet();let d=0;
  document.querySelectorAll('#t tbody tr').forEach(tr=>{
    const st=eff(tr,ls); tr.dataset.status=st; if(st==='done')d++;
    const b=tr.querySelector('.sbadge'),m=META[st]; b.textContent=m[0];b.style.color=m[1];b.style.background=m[2];});
  const n=document.querySelectorAll('#t tbody tr').length;
  document.getElementById('done').textContent=d+' / '+n+' done';
  document.getElementById('bar').style.width=(n?Math.round(d*100/n):0)+'%';
}
function markOpen(id){const ls=lsGet(); if(ls[id]!=='done'){ls[id]='open';lsSet(ls);} applyStatuses();}
const q=document.getElementById('q'),st=document.getElementById('st'),df=document.getElementById('df'),
      pr=document.getElementById('pr'),sf=document.getElementById('sf');
function flt(){const Q=q.value.toLowerCase();let n=0;
  document.querySelectorAll('#t tbody tr').forEach(tr=>{
    const ok=(!Q||tr.dataset.b.includes(Q))&&(!st.value||tr.dataset.s===st.value)&&
      (!df.value||tr.dataset.d===df.value)&&(!pr.value||tr.dataset.p===pr.value)&&
      (!sf.value||tr.dataset.status===sf.value);
    tr.classList.toggle('hide',!ok); if(ok)n++;});
  document.getElementById('cnt').textContent=n+' shown';}
function saveState(){localStorage.setItem(FKEY,JSON.stringify(
  {q:q.value,st:st.value,df:df.value,pr:pr.value,sf:sf.value,y:window.scrollY}));}
function restoreState(){try{const s=JSON.parse(localStorage.getItem(FKEY)||'{}');
  q.value=s.q||'';st.value=s.st||'';df.value=s.df||'';pr.value=s.pr||'';sf.value=s.sf||'';
  applyStatuses();flt(); if(s.y)window.scrollTo(0,s.y);}catch(e){applyStatuses();flt();}}
restoreState();
// auto-refresh: re-read the file so extension/submit status changes appear; pause while typing
const ar=document.getElementById('auto');
setInterval(()=>{const a=document.activeElement;
  if(ar.checked && !(a&&(a.tagName==='INPUT'||a.tagName==='SELECT'))){saveState();location.reload();}},6000);
window.addEventListener('beforeunload',saveState);
</script></body></html>""")
    out = os.path.join(ROOT, "launchpad.html")
    open(out, "w").write("".join(parts))
    return out


def main():
    rows = load_problems()
    status = load_status(rows)
    save_status(status)
    render_launchpad(rows, status)
    est = sum(1 for r in rows if r["difficultyEst"])
    done = sum(1 for v in status.values() if v == "done")
    print(f"rendered launchpad.html + problems.json ({len(rows)} problems, "
          f"{len(rows)-est} real difficulty, {est} estimated, {done} done)")


if __name__ == "__main__":
    main()
