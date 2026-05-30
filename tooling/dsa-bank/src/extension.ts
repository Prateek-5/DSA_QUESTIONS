import * as vscode from "vscode";
import * as https from "https";
import * as path from "path";
import { execFile } from "child_process";

const LANG_EXT: Record<string, string> = {
  cpp: "cpp", python3: "py", java: "java", javascript: "js",
};

interface OpenParams {
  id: string; topic: string; slug: string; title: string;
  leetslug: string; kind: string; src: string; ref: string;
}

export function activate(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.window.registerUriHandler({
      handleUri: (uri: vscode.Uri) => handleUri(uri).catch(showErr),
    }),
    vscode.commands.registerCommand("dsa-bank.submitPush", () =>
      runScriptOnActiveFile("lc-submit.sh", "DSA Submit & Push")),
    vscode.commands.registerCommand("dsa-bank.test", () =>
      runScriptOnActiveFile("lc-test.sh", "DSA Test")),
    vscode.commands.registerCommand("dsa-bank.newApproach", () =>
      runScriptOnActiveFile("new-approach.sh", "DSA New Approach")),
    vscode.commands.registerCommand("dsa-bank.openLaunchpad", openLaunchpad),
  );
  console.log("dsa-bank activated");
}

export function deactivate() {}

function showErr(e: any) {
  vscode.window.showErrorMessage(`DSA Bank: ${e?.message ?? e}`);
}

function repoRoot(): vscode.Uri {
  const ws = vscode.workspace.workspaceFolders;
  if (!ws || ws.length === 0) {
    throw new Error("Open the DSA_QUESTIONS folder in VS Code first.");
  }
  return ws[0].uri;
}

function parseParams(uri: vscode.Uri): OpenParams {
  const q = new URLSearchParams(uri.query);
  const get = (k: string) => q.get(k) ?? "";
  return {
    id: get("id"), topic: get("topic"), slug: get("slug"), title: get("title"),
    leetslug: get("leetslug"), kind: get("kind"), src: get("src"), ref: get("ref"),
  };
}

// minimal GraphQL POST to LeetCode (public, no auth needed for description/snippets)
function leetcodeQuery(slug: string): Promise<any> {
  const body = JSON.stringify({
    query: `query q($s:String!){question(titleSlug:$s){questionFrontendId title difficulty content codeSnippets{langSlug code}}}`,
    variables: { s: slug },
  });
  return new Promise((resolve, reject) => {
    const req = https.request(
      "https://leetcode.com/graphql",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Content-Length": Buffer.byteLength(body),
          "User-Agent": "Mozilla/5.0",
          Referer: "https://leetcode.com",
        },
      },
      (res) => {
        let data = "";
        res.on("data", (c) => (data += c));
        res.on("end", () => {
          try {
            resolve(JSON.parse(data)?.data?.question ?? null);
          } catch (e) {
            reject(e);
          }
        });
      },
    );
    req.on("error", reject);
    req.write(body);
    req.end();
  });
}

async function exists(uri: vscode.Uri): Promise<boolean> {
  try {
    await vscode.workspace.fs.stat(uri);
    return true;
  } catch {
    return false;
  }
}

async function writeFile(uri: vscode.Uri, content: string) {
  await vscode.workspace.fs.writeFile(uri, Buffer.from(content, "utf8"));
}

function cppTemplate(frontendId: string, title: string, snippet: string): string {
  const code = snippet || "class Solution {\npublic:\n    \n};";
  return [
    "/*",
    ` * @lc app=leetcode id=${frontendId} lang=cpp`,
    " *",
    ` * [${frontendId}] ${title}`,
    " */",
    "",
    "// @lc code=start",
    code,
    "// @lc code=end",
    "",
  ].join("\n");
}

function readmeFor(p: OpenParams, q: any): string {
  const diff = q?.difficulty ?? "—";
  const fid = q?.questionFrontendId ? `#${q.questionFrontendId} · ` : "";
  const links: string[] = [];
  if (p.src) links.push(`[Problem](${p.src})`);
  if (p.ref) links.push(`[Reference card](${p.ref})`);
  const head = [
    `# ${fid}${p.title}`,
    "",
    `**Difficulty:** ${diff}  ·  **Topic:** ${p.topic.replace(/_/g, " ")}  ·  ${links.join("  ·  ")}`,
    "",
    "---",
    "",
  ].join("\n");
  if (q?.content) return head + q.content + "\n";
  return (
    head +
    "_No LeetCode description (this is a GeeksforGeeks / misc problem)._ " +
    `Open the [source](${p.src}) and paste the statement here, then solve in \`solution.${LANG_EXT.cpp}\`.\n`
  );
}

async function handleUri(uri: vscode.Uri) {
  if (!uri.path.startsWith("/open")) {
    throw new Error(`Unknown action: ${uri.path}`);
  }
  const p = parseParams(uri);
  if (!p.id || !p.topic || !p.slug) {
    throw new Error("Link is missing id/topic/slug.");
  }
  const root = repoRoot();
  const lang = vscode.workspace.getConfiguration("dsaBank").get<string>("defaultLanguage", "cpp");
  const ext = LANG_EXT[lang] ?? "cpp";
  const folder = vscode.Uri.joinPath(root, "DSA", "Solutions", p.topic, `${p.id}-${p.slug}`);
  const readme = vscode.Uri.joinPath(folder, "README.md");
  const sol = vscode.Uri.joinPath(folder, `solution.${ext}`);

  const fresh = !(await exists(sol));
  if (fresh) {
    await vscode.workspace.fs.createDirectory(folder);
    let q: any = null;
    if (p.kind === "leetcode" && p.leetslug) {
      await vscode.window.withProgress(
        { location: vscode.ProgressLocation.Notification, title: `Fetching “${p.title}” from LeetCode…` },
        async () => {
          try {
            q = await leetcodeQuery(p.leetslug);
          } catch (e) {
            vscode.window.showWarningMessage(`DSA Bank: could not fetch description (${e}). Scaffolding blank.`);
          }
        },
      );
    }
    await writeFile(readme, readmeFor(p, q));
    const snippet =
      (q?.codeSnippets ?? []).find((c: any) => c.langSlug === (lang === "cpp" ? "cpp" : lang))?.code ?? "";
    const fid = q?.questionFrontendId ?? p.id;
    await writeFile(sol, lang === "cpp" ? cppTemplate(fid, p.title, snippet) : (snippet || ""));
  }

  // open description (preview) + solution side by side
  await vscode.commands.executeCommand("markdown.showPreviewToSide", readme).then(undefined, () => {});
  const doc = await vscode.workspace.openTextDocument(sol);
  await vscode.window.showTextDocument(doc, { viewColumn: vscode.ViewColumn.One, preview: false });

  // mark this problem "In Progress" in the launchpad
  setStatus(root.fsPath, p.id, "open");

  vscode.window.setStatusBarMessage(
    fresh ? `DSA Bank: scaffolded ${p.id}-${p.slug}` : `DSA Bank: opened ${p.id}-${p.slug}`,
    4000,
  );
}

function setStatus(root: string, id: string, status: string) {
  execFile("python3", [path.join(root, "tooling", "set-status.py"), id, status], (err) => {
    if (err) console.log(`dsa-bank: set-status failed: ${err.message}`);
  });
}

async function runScriptOnActiveFile(script: string, termName: string) {
  const ed = vscode.window.activeTextEditor;
  if (!ed) {
    throw new Error("Open a solution file first.");
  }
  await ed.document.save();
  const file = ed.document.uri.fsPath;
  const scriptPath = path.join(repoRoot().fsPath, "tooling", script);
  const term =
    vscode.window.terminals.find((t) => t.name === termName) ??
    vscode.window.createTerminal(termName);
  term.show();
  term.sendText(`bash "${scriptPath}" "${file}"`);
}

async function openLaunchpad() {
  const root = repoRoot();
  const lp = vscode.Uri.joinPath(root, "launchpad.html");
  await vscode.env.openExternal(lp);
}
