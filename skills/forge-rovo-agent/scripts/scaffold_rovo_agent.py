#!/usr/bin/env python3
"""
Forge Rovo Agent Scaffold Script

Creates a new Forge app with rovo:agent + action + function module boilerplate:
  - manifest.yml with a rovo:agent module, its actions, and backing functions
  - src/index.js with an exported handler per action

Grounded in the Forge manifest reference:
  https://developer.atlassian.com/platform/forge/manifest-reference/modules/rovo-agent/
  https://developer.atlassian.com/platform/forge/manifest-reference/modules/rovo-action/

Run from the skill directory (the directory containing SKILL.md):
    python3 -m scripts.scaffold_rovo_agent \
        --name my-rovo-agent \
        --agent-name "Risk Assistant" \
        --prompt "You help users manage project risks." \
        --dev-space-id <id> \
        --directory /path/to/parent
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

# rovo:agent / action manifest constraints (from the manifest reference).
VALID_ACTION_VERBS = ("GET", "CREATE", "UPDATE", "DELETE", "TRIGGER")
VALID_INPUT_TYPES = ("string", "integer", "number", "boolean")
MAX_AGENT_NAME = 30  # rovo:agent `name` must not exceed 30 characters.
KEY_RE = re.compile(r"^[a-zA-Z0-9_-]+$")  # Forge module key regex
JS_ID_RE = re.compile(r"^[A-Za-z_$][A-Za-z0-9_$]*$")  # action `function` becomes a JS export name


def _yaml_str(value):
    s = str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\t", "\\t")
    return f'"{s}"'


def _validate(agent, actions):
    name = agent.get("name", "")
    if not name or len(name) > MAX_AGENT_NAME:
        raise ValueError(
            f"Agent name must be 1-{MAX_AGENT_NAME} characters (got {len(name)})."
        )
    if not KEY_RE.match(agent.get("key", "")):
        raise ValueError(f"Agent key {agent.get('key')!r} must match {KEY_RE.pattern}.")
    for a in actions:
        if not KEY_RE.match(a.get("key", "")):
            raise ValueError(f"Action key {a.get('key')!r} must match {KEY_RE.pattern}.")
        if not JS_ID_RE.match(a.get("function", "")):
            raise ValueError(
                f"Action function {a.get('function')!r} must be a valid JavaScript identifier."
            )
        if a.get("action_verb") not in VALID_ACTION_VERBS:
            raise ValueError(
                f"Invalid actionVerb {a.get('action_verb')!r}; "
                f"must be one of {', '.join(VALID_ACTION_VERBS)}."
            )
        for in_name, spec in (a.get("inputs") or {}).items():
            if not KEY_RE.match(in_name):
                raise ValueError(f"Input name {in_name!r} must match {KEY_RE.pattern}.")
            if spec.get("type") not in VALID_INPUT_TYPES:
                raise ValueError(
                    f"Invalid input type {spec.get('type')!r} for input {in_name!r}; "
                    f"must be one of {', '.join(VALID_INPUT_TYPES)}."
                )


def build_manifest(app_id, agent, actions):
    """Build a manifest.yml string with rovo:agent + action + function modules.

    agent:   {key, name, prompt, description?, conversation_starters?}
    actions: [{key, name, function, action_verb, description, inputs}]
             inputs: {input_name: {title, type, required, description?}}
    """
    _validate(agent, actions)
    out = []
    out.append("app:")
    out.append(f'  id: "{app_id}"')
    out.append("  runtime:")
    out.append("    name: nodejs24.x")
    out.append("")
    out.append("permissions:")
    out.append("  scopes: []")
    out.append("")
    out.append("modules:")

    out.append("  rovo:agent:")
    out.append(f'    - key: {agent["key"]}')
    out.append(f'      name: {_yaml_str(agent["name"])}')
    if agent.get("description"):
        out.append(f'      description: {_yaml_str(agent["description"])}')
    out.append("      prompt: |")
    for line in (agent.get("prompt") or "").splitlines() or [""]:
        out.append(f"        {line}")
    starters = agent.get("conversation_starters") or []
    if starters:
        out.append("      conversationStarters:")
        for s in starters:
            out.append(f"        - {_yaml_str(s)}")
    if actions:
        out.append("      actions:")
        for a in actions:
            out.append(f'        - {a["key"]}')

    if actions:
        out.append("  action:")
        for a in actions:
            out.append(f'    - key: {a["key"]}')
            out.append(f'      name: {_yaml_str(a["name"])}')
            out.append(f'      function: {a["function"]}')
            out.append(f'      actionVerb: {a["action_verb"]}')
            out.append(f'      description: {_yaml_str(a["description"])}')
            inputs = a.get("inputs") or {}
            if inputs:
                out.append("      inputs:")
                for in_name, spec in inputs.items():
                    out.append(f"        {in_name}:")
                    out.append(f'          title: {_yaml_str(spec["title"])}')
                    out.append(f'          type: {spec["type"]}')
                    out.append(f'          required: {str(spec["required"]).lower()}')
                    if spec.get("description"):
                        out.append(f'          description: {_yaml_str(spec["description"])}')

        out.append("  function:")
        for a in actions:
            out.append(f'    - key: {a["function"]}')
            out.append(f'      handler: index.{a["function"]}')

    return "\n".join(out) + "\n"


def build_index_js(actions):
    if not actions:
        return "// No actions defined yet. Add actions and re-run the scaffold.\n"
    blocks = ["import api, { route } from '@forge/api';"]
    for a in actions:
        fn = a["function"]
        blocks.append(
            f"""export const {fn} = async (payload) => {{
  // Rovo passes the inputs it extracted from the user under `payload`.
  // TODO: implement '{a.get("name", fn)}' and return a JSON-serialisable result.
  console.log('[{fn}] invoked with', JSON.stringify(payload));
  return {{ message: 'TODO: implement {fn}' }};
}};"""
        )
    return "\n\n".join(blocks) + "\n"


def check_prerequisites():
    for tool in ("node", "forge"):
        try:
            subprocess.run([tool, "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"❌ '{tool}' not found. Install Node.js 22+ and Forge CLI (npm install -g @forge/cli).")
            return False
    return True


def run_forge_create(app_name, cwd, dev_space_id):
    cmd = ["forge", "create", "--template", "blank", app_name, "--accept-terms"]
    if dev_space_id:
        cmd += ["--developer-space-id", dev_space_id]
    print(f"\n📦 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ forge create failed (exit {result.returncode})")
        if result.stdout.strip():
            print(f"\n--- stdout ---\n{result.stdout.strip()}")
        if result.stderr.strip():
            print(f"\n--- stderr ---\n{result.stderr.strip()}")
        return False
    print("✅ forge create succeeded")
    return True


def _existing_app_id(app_dir):
    manifest_path = Path(app_dir) / "manifest.yml"
    if manifest_path.exists():
        for line in manifest_path.read_text().splitlines():
            if "id:" in line:
                return line.split("id:")[-1].strip().strip('"')
    return ""


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a Forge Rovo Agent app (rovo:agent + action + function)."
    )
    parser.add_argument("--name", required=True, help="App directory name (e.g. my-rovo-agent)")
    parser.add_argument("--agent-name", required=True, help="Agent display name (<= 30 chars)")
    parser.add_argument("--agent-key", default=None, help="Agent module key (default: derived from --name)")
    parser.add_argument("--prompt", required=True, help="The agent's LLM instructions/prompt")
    parser.add_argument("--dev-space-id", default=None, help="Forge developer space ID (optional)")
    parser.add_argument("--directory", default=None, help="Parent directory (default: current dir)")
    args = parser.parse_args()

    agent_key = (args.agent_key or args.name).lower().replace(" ", "-")
    agent = {
        "key": agent_key,
        "name": args.agent_name,
        "description": f"{args.agent_name} — a Forge Rovo Agent.",
        "prompt": args.prompt,
        "conversation_starters": ["What can you do?"],
    }
    actions = [
        {
            "key": "example-action",
            "name": "Example action",
            "function": "exampleAction",
            "action_verb": "GET",
            "description": "Example read-only action. Replace with your real action.",
            "inputs": {
                "query": {
                    "title": "Query",
                    "type": "string",
                    "required": True,
                    "description": "What the user is asking for",
                }
            },
        }
    ]

    try:
        _validate(agent, actions)
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)

    if not check_prerequisites():
        sys.exit(1)

    parent_dir = os.path.abspath(args.directory) if args.directory else os.getcwd()
    app_dir = os.path.join(parent_dir, args.name)
    if not os.path.isdir(parent_dir):
        print(f"❌ Parent directory does not exist: {parent_dir}")
        sys.exit(1)
    if os.path.exists(app_dir):
        print(f"❌ Directory already exists: {app_dir}")
        sys.exit(1)

    print(f"\n🤖 Scaffolding Forge Rovo Agent: {args.agent_name}")
    if not run_forge_create(args.name, parent_dir, args.dev_space_id):
        print("\n💡 If forge create needs a TTY, run it yourself, then re-run from Step 3 of SKILL.md:")
        print(f"   cd {parent_dir} && forge create --template blank {args.name}")
        sys.exit(1)

    manifest = build_manifest(_existing_app_id(app_dir) or "{}", agent, actions)
    (Path(app_dir) / "manifest.yml").write_text(manifest)
    print("✅ Wrote manifest.yml")

    src_dir = Path(app_dir) / "src"
    src_dir.mkdir(exist_ok=True)
    (src_dir / "index.js").write_text(build_index_js(actions))
    print("✅ Wrote src/index.js")

    print(f"\n{'=' * 60}")
    print("✅ Rovo Agent scaffolded!")
    print(f"\nNext steps:")
    print(f"  1. cd {app_dir} && npm install")
    print(f"  2. Refine the prompt in manifest.yml and implement src/index.js")
    print(f"  3. Add more actions (see SKILL.md), then: forge lint")
    print(f"  4. Deploy with the forge-app-builder deploy script, then enable the agent in Rovo")


if __name__ == "__main__":
    main()
