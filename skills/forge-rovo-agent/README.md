# Forge Rovo Agent Skill

Builds Atlassian Forge **Rovo Agents** — configurable AI teammates that integrate into Jira and Confluence using the `rovo:agent` and `action` Forge modules.

Use this skill when you want an agent to scaffold and wire a Rovo agent: write the prompt, define actions (Forge functions the agent can call), and implement the handlers.

## What This Skill Does

Guides the full Rovo agent workflow:

1. Define the agent's purpose, prompt, and actions with the user
2. Scaffold a `rovo:agent` app from the `blank` template (`scripts/scaffold_rovo_agent.py`)
3. Configure `manifest.yml` — `rovo:agent`, `action`, and `function` modules
4. Implement each action handler in `src/index.js`
5. Deploy/install (via the forge-app-builder deploy script)
6. Test the agent in the Rovo chat side panel, the `/ai` editor toolbar, or automation rules

## Use For

- Building a Rovo agent / AI teammate for Jira or Confluence
- Defining agent actions (fetch data, create/update records)
- Writing agent prompts and conversation starters

## Do Not Use For

- Ingesting external data into Rovo Search / Teamwork Graph → use **forge-connector**
- Creating or deploying a generic Forge app → use **forge-app-builder**
- Non-Rovo Jira/Confluence UI modules (panels, macros, pages)

## Prerequisites

- **Node.js 22+** — `node -v`
- **Forge CLI** — `npm install -g @forge/cli`
- **Forge login** — `forge login`

## Quick Start

```bash
# From the forge-rovo-agent skill directory:
python3 -m scripts.scaffold_rovo_agent \
  --name my-rovo-agent \
  --agent-name "Risk Assistant" \
  --prompt "You help users manage project risks." \
  --dev-space-id <your-dev-space-id> \
  --directory ~/projects
```

## Module Essentials

- `rovo:agent` — the agent: `key`, `name` (≤30 chars), `prompt`, optional `conversationStarters`, and a list of `actions`.
- `action` — a task the agent can run: `function`, `actionVerb` (GET/CREATE/UPDATE/DELETE/TRIGGER), `description` (the agent uses this to decide when to call it), and typed `inputs`.
- `function` — the backing Forge function whose `handler` (`index.<export>`) implements the action. Actions can process up to 5 MB.

## Scripts

| Script | Purpose |
|---|---|
| `scripts/scaffold_rovo_agent.py` | Scaffold a `rovo:agent` app: manifest + handler boilerplate |

## Further Reading

- [rovo:agent module reference](https://developer.atlassian.com/platform/forge/manifest-reference/modules/rovo-agent/)
- [action module reference](https://developer.atlassian.com/platform/forge/manifest-reference/modules/rovo-action/)
- [Extend Atlassian apps with a Forge Rovo Agent](https://developer.atlassian.com/platform/forge/)

See [SKILL.md](SKILL.md) for the full workflow and manifest reference.
