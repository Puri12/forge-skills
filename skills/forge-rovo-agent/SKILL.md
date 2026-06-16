---
name: forge-rovo-agent
description: >
  Builds Atlassian Forge Rovo Agents — configurable AI teammates that integrate into Jira and
  Confluence using the `rovo:agent` and `action` Forge modules. Use when the user wants to create a
  Rovo agent, add an AI teammate/assistant to Jira or Confluence, define agent actions (functions the
  agent can call), write an agent prompt, add conversation starters, or wire a Forge function so an
  agent can fetch data or perform operations. Do not use for ingesting external data into Rovo Search
  / Teamwork Graph (use forge-connector), for general app scaffolding (use forge-app-builder), or for
  non-Rovo Jira/Confluence UI modules.
license: Apache-2.0
labels:
  - forge
  - rovo
  - ai
  - jira
  - confluence
  - atlassian
maintainer: atlassian-developer
namespace: cloud
---

# Forge Rovo Agent

Build a Forge **Rovo Agent**: an AI teammate defined by a `rovo:agent` module (a prompt) plus one or more `action` modules (Forge functions the agent can invoke to fetch data or perform operations).

**When building a Rovo agent, complete the workflow in order. Run the scripts yourself; do not only hand the user manual commands.**

## Critical Rules

1. **Agent `name` ≤ 30 characters** — longer names fail `forge lint`. Keep it short and human-friendly.
2. **Action `description` is how the agent decides when to call it** — write it for the LLM, not for humans. Be explicit about what the action does and when to use it.
3. **`actionVerb` controls automation** — agents triggered by **automation rules only invoke `GET` actions**. `CREATE`, `UPDATE`, `DELETE`, `TRIGGER` actions are skipped in automation. Pick the verb that matches the real effect.
4. **Actions are Forge functions** — every action references a `function`, whose `handler` is `index.<exportName>`. The handler receives the inputs the agent extracted from the user.
5. **App-based agents only see data in the workspace where the app is installed.** A Jira-installed agent cannot read Confluence data unless the app is configured for multiple products (App compatibility).
6. **Action data limit is 5 MB** — segment or summarize large datasets before returning them.
7. **Never ask for credentials in chat** — direct users to run `forge login` in their own terminal.
8. **Always run the scaffold script yourself** — do not only print manual instructions.
9. **Rovo Acceptable Use Policy applies** — Atlassian safety-screens agents and may block deployment. Keep prompts and actions within policy.

## MCP Prerequisites

| MCP Server    | Purpose                                                        |
| ------------- | -------------------------------------------------------------- |
| **Forge MCP** | Latest `rovo:agent` / `action` manifest syntax, scopes, guides |

If Forge MCP is unavailable, verify against [the rovo:agent reference](https://developer.atlassian.com/platform/forge/manifest-reference/modules/rovo-agent/) and [the action reference](https://developer.atlassian.com/platform/forge/manifest-reference/modules/rovo-action/).

## Agent Workflow — complete Steps 0–6 in order

### Step 0: Prerequisites

Check Node.js (`node -v`, 22+), Forge CLI (`forge --version`), and login (`forge whoami`). Install missing tools with `npm install -g @forge/cli`. If not logged in, tell the user to run `forge login` in their own terminal (never paste tokens in chat).

### Step 1: Define the agent with the user

Before scaffolding, agree on:

- **Purpose** — one sentence on what the teammate does.
- **Prompt** — the agent's behavior/instructions (the LLM system prompt).
- **Actions** — each capability the agent needs (fetch X, create Y…), with the right `actionVerb` and inputs.
- **Product** — Jira, Confluence, or both (affects data access and scopes).

### Step 2: Discover the developer space

`forge create` needs an interactive TTY to select a developer space. If you know the `--dev-space-id`, pass it to the scaffold (Step 3). Otherwise ask the user to run `forge create --template blank <name>` in their terminal; then wire the agent **manually** from the manifest reference below (Steps 4–5) — the scaffold only creates a brand-new app, so it can't run against an already-created directory.

### Step 3: Scaffold the agent

Run from the **skill directory** (the directory containing this SKILL.md):

```bash
python3 -m scripts.scaffold_rovo_agent \
  --name <app-name> \
  --agent-name "<Agent Name ≤30 chars>" \
  --prompt "<the agent's instructions>" \
  --dev-space-id <id> \
  --directory <parent-directory>
```

This runs `forge create --template blank`, then writes a `manifest.yml` with a `rovo:agent` + a starter `action` + backing `function`, and a `src/index.js` with one exported handler per action.

### Step 4: Refine the prompt and actions

Edit `manifest.yml`:

- Tighten the `prompt`. For long prompts, move it to a resource file: `prompt: resource:agent;prompts/agent.txt` (requires Forge CLI 10.6.0+) and add the `resources` entry.
- Add the real `action` entries the agent needs. Each action needs `key`, `name`, `function`, `actionVerb`, `description`, and `inputs`. Reference every action key from the agent's `actions` list.

### Step 5: Implement the handlers

Edit `src/index.js`. Each action's `function` maps to an exported handler `index.<function>`. The handler receives the agent-extracted inputs as its **first** argument; the invocation `context` (including the user `accountId`) is the second:

```javascript
export const fetchRisks = async (payload) => {
  const { projectKey } = payload;
  // call Jira/Confluence via @forge/api, then return a JSON-serialisable result (< 5 MB)
  return { risks: [] };
};
```

### Step 6: Deploy, then enable and test the agent

Deploy and install using the **forge-app-builder** deploy script (`python3 -m scripts.deploy_forge_app` from that skill's directory). Then test the agent via:

- **Chat side panel** — the **Chat** button in Jira/Confluence top navigation.
- **AI toolbar** — `/ai` in the Jira or Confluence editor.
- **Automation** — add the agent to an automation rule (GET actions only).

## Manifest reference (grounded)

### `rovo:agent`

| Property | Required | Notes |
|---|---|---|
| `key` | yes | Unique; regex `^[a-zA-Z0-9_-]+$` |
| `name` | yes | **≤ 30 characters** |
| `description` | no | Shown to users |
| `icon` | no | Resource path or absolute URL |
| `prompt` | yes | String, or `resource:<key>;<path>` (CLI 10.6.0+) |
| `conversationStarters` | no | Suggested prompts (string list) |
| `actions` | no | List of `action` module keys |
| `followUpPrompt` | no | Generates follow-up suggestions |

### `action`

| Property | Required | Notes |
|---|---|---|
| `key` | yes | Unique |
| `name` | yes | Shown in UI |
| `function` | yes | Backing function key (`endpoint` instead, for Forge Remote) |
| `actionVerb` | yes | `GET` \| `CREATE` \| `UPDATE` \| `DELETE` \| `TRIGGER` — automation only runs `GET` |
| `description` | yes | The agent reads this to decide when to invoke |
| `inputs` | yes | `{ inputName: { title, type, required, description } }`; `type` ∈ string/integer/number/boolean |

Each `function` entry has `key` + `handler` (`index.<export>`). Actions can process up to **5 MB**. The scaffold sets `app.runtime.name: nodejs24.x`.

**Scopes:** an agent that only calls its own bundled actions needs no extra scopes. If an action calls an Atlassian REST API, add the matching scope. To let **customer-built** agents invoke your actions, add `read:chat:rovo`.

## Scripts

| Script | Purpose |
|---|---|
| `scripts/scaffold_rovo_agent.py` | Scaffold a `rovo:agent` app (manifest + handlers). Run: `python3 -m scripts.scaffold_rovo_agent` |

## Common mistakes (avoid these)

- Agent `name` over 30 characters (lint failure).
- Vague action `description` — the agent then never picks the action.
- Using `CREATE`/`UPDATE` actions and expecting automation rules to call them (they only call `GET`).
- Handler reading `event.payload` — action handlers receive inputs as the **first argument**, not nested under `event.payload`.
- Expecting a Jira agent to read Confluence data without multi-product app configuration.

## Example triggers

- "Build a Rovo agent that summarizes my open Jira issues"
- "Add an AI teammate to Confluence that drafts release notes"
- "Create a Rovo action that creates a Jira issue from a description"
- "Write the prompt and actions for a risk-management agent"
