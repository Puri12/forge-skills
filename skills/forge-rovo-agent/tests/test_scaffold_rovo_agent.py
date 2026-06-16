"""
Tests for scripts/scaffold_rovo_agent.py

Grounded in the Forge manifest reference for the rovo:agent and action modules:
  https://developer.atlassian.com/platform/forge/manifest-reference/modules/rovo-agent/
  https://developer.atlassian.com/platform/forge/manifest-reference/modules/rovo-action/
"""
import unittest

from scripts import scaffold_rovo_agent as sra


SAMPLE_AGENT = {
    "key": "risk-agent",
    "name": "Risk Register Assistant",
    "description": "Helps manage project risks",
    "prompt": "You are a helpful assistant that helps users manage project risks.",
    "conversation_starters": ["Fetch my active risks", "Create a new risk"],
}

SAMPLE_ACTIONS = [
    {
        "key": "fetch-risks",
        "name": "Fetch risks",
        "function": "fetchRisks",
        "action_verb": "GET",
        "description": "Retrieve all project risks",
        "inputs": {
            "projectKey": {
                "title": "Project key",
                "type": "string",
                "required": True,
                "description": "The project to fetch risks for",
            }
        },
    },
    {
        "key": "create-risk",
        "name": "Create risk",
        "function": "createRisk",
        "action_verb": "CREATE",
        "description": "Create a new project risk",
        "inputs": {
            "summary": {
                "title": "Summary",
                "type": "string",
                "required": True,
                "description": "Risk summary",
            }
        },
    },
]


class TestBuildManifest(unittest.TestCase):
    def test_contains_rovo_agent_block(self):
        m = sra.build_manifest("ari:cloud:ecosystem::app/abc", SAMPLE_AGENT, SAMPLE_ACTIONS)
        self.assertIn("rovo:agent:", m)
        self.assertIn("key: risk-agent", m)
        self.assertIn("Risk Register Assistant", m)
        self.assertIn("prompt:", m)
        self.assertIn("conversationStarters:", m)
        self.assertIn("Fetch my active risks", m)

    def test_agent_references_all_action_keys(self):
        m = sra.build_manifest("app-id", SAMPLE_AGENT, SAMPLE_ACTIONS)
        # the agent's actions list must reference each action key
        agent_actions_section = m.split("actions:")[1]
        self.assertIn("fetch-risks", agent_actions_section)
        self.assertIn("create-risk", agent_actions_section)

    def test_contains_action_and_function_modules(self):
        m = sra.build_manifest("app-id", SAMPLE_AGENT, SAMPLE_ACTIONS)
        self.assertIn("action:", m)
        self.assertIn("actionVerb: GET", m)
        self.assertIn("actionVerb: CREATE", m)
        self.assertIn("function: fetchRisks", m)
        # inputs rendered with title/type/required
        self.assertIn("projectKey:", m)
        self.assertIn('title: "Project key"', m)
        self.assertIn("type: string", m)
        self.assertIn("required: true", m)
        # function module with handler index.<function>
        self.assertIn("function:", m)
        self.assertIn("handler: index.fetchRisks", m)
        self.assertIn("handler: index.createRisk", m)

    def test_invalid_action_verb_raises(self):
        bad = [dict(SAMPLE_ACTIONS[0], action_verb="FETCH")]
        with self.assertRaises(ValueError):
            sra.build_manifest("app-id", SAMPLE_AGENT, bad)

    def test_agent_name_too_long_raises(self):
        bad_agent = dict(SAMPLE_AGENT, name="x" * 31)  # rovo:agent name must be <= 30 chars
        with self.assertRaises(ValueError):
            sra.build_manifest("app-id", bad_agent, SAMPLE_ACTIONS)

    def test_invalid_input_type_raises(self):
        bad_action = dict(SAMPLE_ACTIONS[0])
        bad_action["inputs"] = {"d": {"title": "D", "type": "date", "required": True, "description": "x"}}
        with self.assertRaises(ValueError):
            sra.build_manifest("app-id", SAMPLE_AGENT, [bad_action])

    def test_manifest_includes_runtime(self):
        m = sra.build_manifest("app-id", SAMPLE_AGENT, SAMPLE_ACTIONS)
        self.assertIn("runtime:", m)
        self.assertIn("nodejs24.x", m)

    def test_special_characters_are_quoted(self):
        agent = dict(SAMPLE_AGENT, name="Risk: agent #1")
        m = sra.build_manifest("app-id", agent, SAMPLE_ACTIONS)
        self.assertIn('name: "Risk: agent #1"', m)

    def test_invalid_agent_key_raises(self):
        bad = dict(SAMPLE_AGENT, key="bad key!")
        with self.assertRaises(ValueError):
            sra.build_manifest("app-id", bad, SAMPLE_ACTIONS)

    def test_invalid_function_name_raises(self):
        bad = [dict(SAMPLE_ACTIONS[0], function="123-not-js")]
        with self.assertRaises(ValueError):
            sra.build_manifest("app-id", SAMPLE_AGENT, bad)

    def test_invalid_input_name_raises(self):
        bad = [dict(SAMPLE_ACTIONS[0], inputs={"bad: name": {"title": "B", "type": "string", "required": True, "description": "x"}})]
        with self.assertRaises(ValueError):
            sra.build_manifest("app-id", SAMPLE_AGENT, bad)


class TestBuildIndexJs(unittest.TestCase):
    def test_exports_a_handler_per_action(self):
        js = sra.build_index_js(SAMPLE_ACTIONS)
        self.assertIn("export const fetchRisks", js)
        self.assertIn("export const createRisk", js)

    def test_empty_actions_produces_no_handlers(self):
        js = sra.build_index_js([])
        self.assertNotIn("export const", js)


if __name__ == "__main__":
    unittest.main()
