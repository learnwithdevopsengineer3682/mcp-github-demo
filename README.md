# MCP + GitHub Actions: Investigate a Failed Pipeline

**LearnWithDevOpsEngineer** · Beginner-friendly hands-on lab

## The incident

| System | Status | Goal |
|---|---|---|
| Python pricing app | Running locally | Calculate discounted prices |
| GitHub Actions CI | ❌ Test failure | Find the failing assertion |
| GitHub MCP integration | To be connected | Retrieve workflow evidence |
| Engineer | In control | Validate, fix, verify |

```text
PUSH → GITHUB ACTIONS → PYTEST → ❌ FAILED
                                      │
                                      ▼
                              Investigate → Fix → Re-run → ✅
```

## Contents

- [Prerequisites](#0-before-you-start)
- [Project files](#project-files)
- [Reproduce the failure](#1-reproduce-the-failure)
- [GitHub Actions](#2-run-it-in-github-actions)
- [MCP architecture](#4-mcp-architecture)
- [Connect GitHub MCP in VS Code](#5-connect-github-mcp-in-vs-code)
- [Investigate through MCP](#6-investigate-through-mcp)
- [Apply and verify the fix](#7-apply-the-smallest-fix)

## 0. Before you start

| Requirement | Verify | Link |
|---|---|---|
| Git | `git --version` | [Install Git](https://git-scm.com/downloads) |
| Python 3.11+ | `python --version` | [Install Python](https://www.python.org/downloads/) |
| VS Code | Open the editor | [VS Code](https://code.visualstudio.com/) |
| GitHub account | Sign in | [GitHub](https://github.com/) |
| GitHub Copilot Chat | Open Chat in VS Code, use Agent mode | [GitHub Copilot](https://docs.github.com/en/copilot) |

**Not needed for the hosted MCP server:** Docker. Use a dedicated demo repository with no secrets.

## Project files

```text
mcp-github-demo/
├── .github/workflows/ci.yml
├── app/pricing.py
├── tests/test_pricing.py
├── requirements.txt
└── README.md
```

## 1. Reproduce the failure

**Pricing example**

| Original price | Discount | Correct final price |
|---:|---:|---:|
| 100 | 20% | 80 |

**Windows PowerShell**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

**Expected before fix:** `2 passed, 1 failed`

## 2. Run it in GitHub Actions

**Workflow:** [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

```text
Push / Pull Request / Manual Run
                │
                ▼
        Ubuntu runner
                │
          Checkout code
                │
          Setup Python
                │
       Install dependencies
                │
           Run pytest
                │
             ❌ FAIL
```

Create a **new empty repository** named `mcp-github-demo` (do not initialize with a README).

```bash
git init
git add .
git commit -m "Add failing CI investigation lab"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/mcp-github-demo.git
git push -u origin main
```

**GitHub navigation:** Repository → **Actions** → **Python CI** → Failed run → **test** → **Run tests**

## 3. Without MCP vs. with MCP

| Without integration | With an authorized MCP integration |
|---|---|
| Open GitHub Actions manually | Ask an AI assistant to inspect a run |
| Find and copy relevant logs | AI requests available GitHub tools |
| Paste logs into chat | Tool results provide relevant evidence |
| Review suggested fix | Review suggested fix |

```text
WITHOUT MCP
Developer → GitHub UI → Copy logs → AI chat

WITH MCP
Developer → AI Host → MCP Client → GitHub MCP Server → GitHub API
                ▲                                  │
                └────────── Tool results ──────────┘
```

## 4. MCP architecture

**MCP = Model Context Protocol**

```text
                   YOU
                    │
                    ▼
       ┌────────────────────────┐
       │ HOST: VS Code + AI Chat│
       │   AI + MCP Client      │
       └────────────┬───────────┘
                    │ MCP
                    ▼
       ┌────────────────────────┐
       │  GitHub MCP Server     │
       │  Exposes tools         │
       └────────────┬───────────┘
                    │ GitHub API
                    ▼
       ┌────────────────────────┐
       │ GitHub                 │
       │ Repos · Runs · Jobs    │
       └────────────────────────┘
```

| Term | Role |
|---|---|
| Host | AI application managing MCP connections |
| Client | Protocol connection inside the host |
| Server | Exposes authorized capabilities |
| Tools | Callable operations |
| Resources | Readable context |
| Prompts | Reusable prompt templates |

**MCP ≠ AI model** · **MCP ≠ GitHub API** · **MCP ≠ unrestricted access**

## 5. Connect GitHub MCP in VS Code

**Official references:** [GitHub MCP Server](https://github.com/github/github-mcp-server) · [VS Code MCP documentation](https://code.visualstudio.com/docs/copilot/customization/mcp-servers) · [GitHub fine-grained tokens](https://github.com/settings/personal-access-tokens/new)

### 5.1 Give access to the demo repository only

**Recommended for this tutorial: fine-grained personal access token (PAT), read-only.** Open the [new token page](https://github.com/settings/personal-access-tokens/new).

| GitHub token setting | Selection |
|---|---|
| Name | `mcp-demo-readonly` |
| Expiration | 7 days (or another short period) |
| Resource owner | Account owning the demo repository |
| Repository access | **Only select repositories** → `mcp-github-demo` |
| Repository permissions → Actions | **Read-only** |
| Repository permissions → Contents | **Read-only** |
| Repository permissions → Metadata | **Read-only** (mandatory) |

Click **Generate token**. Save the token temporarily in a secure location; **never paste it into code or share it on screen**. If the repo belongs to an organization, its policies or approval requirements may affect access.

**Alternative:** VS Code's hosted GitHub MCP connection supports OAuth sign-in. This is often simpler, but for a tightly scoped lab the repo-specific PAT makes the intended permissions explicit. Choose **one** authentication path; do not configure both at once.

### 5.2 Add the hosted MCP server (no Docker)

**Recommended PAT configuration (per-user VS Code configuration, not a tracked project file):**

1. Open VS Code → **Ctrl + Shift + P** → search **MCP: Add Server**.
2. Select **HTTP**, enter `https://api.githubcopilot.com/mcp/`, and follow the prompts; or create a user-level MCP configuration with the JSON below.
3. Choose a name such as `github` and start the server.
4. When prompted for `github_mcp_pat`, paste the token from Step 5.1. **Never expose this prompt or token.**

```json
{
  "servers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${input:github_mcp_pat}",
        "X-MCP-Readonly": "true",
        "X-MCP-Toolsets": "repos,actions"
      }
    }
  },
  "inputs": [
    {
      "type": "promptString",
      "id": "github_mcp_pat",
      "description": "GitHub Personal Access Token",
      "password": true
    }
  ]
}
```
```
{
  "servers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "X-MCP-Toolsets": "repos,actions",
        "X-MCP-Readonly": "true"
      }
    }
  }
}
```

**Why these headers?** `X-MCP-Readonly` limits the server to read operations. `X-MCP-Toolsets` asks the server to expose repository and Actions capabilities instead of unrelated tools. Token permissions are a separate restriction. If a needed read tool is missing, inspect the [server's current configuration docs](https://github.com/github/github-mcp-server/blob/main/docs/server-configuration.md).

**OAuth alternative (no PAT):** use the same HTTP endpoint without the `Authorization` header or `inputs` section, then use VS Code's sign-in/**Auth** flow. In that case, confirm the authorized account and exposed repositories before proceeding. You can still add the read-only and toolset headers.

**File location note:** VS Code also supports workspace `.vscode/mcp.json`, but putting MCP credentials in a committed teaching repository is risky. Prefer user-level configuration. If using workspace configuration, never store a literal token or commit authentication data.

### 5.3 Validate the connection in Copilot Chat

1. Open **GitHub Copilot Chat** → switch to **Agent** mode.
2. Open **Configure Tools / Tools** and verify the GitHub MCP server appears and that its tools are enabled.
3. Use the following validation prompt (replace `YOUR_USERNAME`):

```text
Use GitHub MCP tools (not local files or terminal commands).
List the latest GitHub Actions workflow runs for
YOUR_USERNAME/mcp-github-demo.
Show the tool name you used and the run status.
Do not modify anything.
```

4. Expand the tool call and confirm it used the **GitHub MCP server**, not the local workspace or a different GitHub integration. If Copilot answers without invoking a GitHub MCP tool, the MCP integration has not been verified.
5. Verify the real workflow run matches GitHub → **Actions**.

**If it doesn't work:** confirm the MCP server is started, PAT is valid, repository is selected, Actions permission is `Read`, `actions` toolset is enabled, and the Copilot chat is in Agent mode. If the server reports auth errors, reauthenticate; never show or print the token while troubleshooting.

### Connection verification checklist

- [ ] GitHub Actions shows the failing workflow.
- [ ] Local tests show `2 passed, 1 failed`.
- [ ] GitHub MCP server is connected and read tools are enabled.
- [ ] Copilot invokes a **GitHub MCP** tool and retrieves the correct run.
- [ ] No tokens or credentials are committed to the repository.

## 6. Investigate through MCP

**Prompt to paste into tool-enabled AI chat:**

```text
Investigate the latest failed GitHub Actions workflow in
YOUR_USERNAME/mcp-github-demo.

Use available GitHub MCP tools to locate the failed run,
identify the failing job/step, and retrieve relevant error
evidence or logs if those tools are available.

Explain the likely root cause and recommend the smallest fix.
Do not edit files, push, rerun workflows, or change settings.
State clearly if any required information is unavailable.
```

**Evidence to look for:**

```text
FAILED tests/test_pricing.py
Expected: 70
Actual:   80.0
```

**Verify on screen:** MCP tool name → tool request → returned evidence → AI explanation

If workflow logs are **not exposed** by the connected tools, inspect them manually in GitHub Actions and say so. Do not present manual log retrieval as an MCP capability.

## 7. Apply the smallest fix

**File:** [`tests/test_pricing.py`](tests/test_pricing.py)

```diff
 def test_twenty_percent_discount():
-    assert final_price(100, 20) == 70
+    assert final_price(100, 20) == 80
```

**Run locally**

```bash
python -m pytest -q
```

**Expected after fix:** `3 passed`

**Push the correction**

```bash
git add tests/test_pricing.py
git commit -m "Fix incorrect discount test expectation"
git push
```

**GitHub navigation:** Actions → New **Python CI** run → Confirm green status

## 8. What MCP did — and did not do

| MCP integration | AI assistant | Engineer |
|---|---|---|
| Exposes authorized GitHub operations | Chooses tools and interprets results | Validates diagnosis |
| Returns available tool data | Suggests a fix | Approves changes |
| Does not guarantee complete logs | Can make mistakes | Verifies CI passes |

## 9. Production safeguards

- Dedicated test repository
- Least-privilege access
- Review tool calls and outputs
- Treat repository content and logs as untrusted
- Never display or commit tokens
- Human approval for changes

---

**LearnWithDevOpsEngineer** · Build → Break → Investigate → Fix → Verify