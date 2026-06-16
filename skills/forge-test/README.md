# Forge Test Skill

Guides **testing** Atlassian Forge apps with a fast, layered strategy: static checks, unit tests with mocked Forge APIs, live testing with `forge tunnel`, frontend/end-to-end tests, and CI wiring.

Use this skill to design or write tests for a Forge app — it is the quality lane, not the incident lane.

## Use For

- Unit-testing resolvers, functions, and Rovo action handlers
- Mocking `@forge/api`, `@forge/bridge`, and `@forge/kvs` in jest / `node --test`
- Live testing with `forge tunnel`
- Frontend tests (UI Kit, Custom UI) and end-to-end flows
- Adding a test job to CI

## Do Not Use For

- Diagnosing a specific observed failure, error, or stack trace → **forge-debugger**
- Creating or deploying an app → **forge-app-builder**
- Pre-release readiness review → **forge-app-review**

## Testing Layers (cheapest first)

| Layer | Tool | Catches |
|-------|------|---------|
| Static | `forge lint` | manifest/handler wiring, scopes |
| Unit | jest / `node --test` + mocks | resolver/function/action logic |
| Live | `forge tunnel` | real runtime behavior, fast iteration |
| End-to-end | dev install + Playwright / manual | the real user flow |

## What It Provides

- A mock cheat-sheet for `@forge/api`, `@forge/kvs`, and `@forge/bridge`.
- Copy-paste resolver and Rovo action handler test examples.
- The `forge tunnel` live-testing workflow (including breakpoint debugging).
- A CI snippet that runs `forge lint` + unit tests without Atlassian credentials.

## Example Prompts

```text
Write unit tests for my Forge resolver and mock @forge/api.
```

```text
Set up forge tunnel so I can test my app live against my dev site.
```

```text
Add a CI job that lints and unit-tests my Forge app.
```

## Further Reading

- [Tunneling](https://developer.atlassian.com/platform/forge/tunneling/)
- [forge tunnel CLI reference](https://developer.atlassian.com/platform/forge/cli-reference/tunnel/)

See [SKILL.md](SKILL.md) for the full layered strategy, mock cheat-sheet, and examples.
