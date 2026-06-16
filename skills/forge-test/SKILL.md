---
name: forge-test
description: >
  Guides testing Atlassian Forge apps: unit-testing resolvers, functions, and Rovo action handlers;
  mocking @forge/api, @forge/bridge, and @forge/kvs; live testing with forge tunnel; frontend tests
  for UI Kit and Custom UI; end-to-end testing; and wiring tests into CI. Use when the user wants to
  test a Forge app, write resolver/function unit tests, mock Forge APIs, set up forge tunnel for
  live testing, add end-to-end tests, or add a test job to CI. Do not use for diagnosing a specific
  observed failure or error (use forge-debugger), or for creating/deploying an app (use
  forge-app-builder).
license: Apache-2.0
labels:
  - forge
  - testing
  - quality
  - atlassian
maintainer: atlassian-developer
namespace: cloud
---

# Forge Test

Set up a fast, layered test strategy for a Forge app. Cheap checks first, real-environment checks last.

## Testing layers (cheapest first)

| Layer | Tool | Catches |
|-------|------|---------|
| 1. Static | `forge lint` | manifest/handler wiring, scope/syntax errors |
| 2. Unit | jest / `node --test` + mocks | resolver/function/action logic |
| 3. Live | `forge tunnel` | real runtime behavior, fast iteration |
| 4. End-to-end | dev install + Playwright / manual | the actual user flow |

## Critical Rules

1. **Run the cheap layer first** — `forge lint` before unit tests; unit tests before deploying.
2. **Mock at the Forge boundary** — unit tests should mock `@forge/api`, `@forge/bridge`, and `@forge/kvs`; never hit real Atlassian APIs in unit tests.
3. **Keep handlers thin and exported** — put business logic in plain, exported functions so it can be tested without the Forge runtime.
4. **Match the runtime** — `forge tunnel` redirects invocations to your **local** code, so match your local Node version to the app's configured Forge runtime (Node.js 24 recommended, or 22; Node 20 is end-of-life). Don't rely on libraries the runtime doesn't provide.
5. **`forge tunnel` is for live testing, not unit tests** — it needs a deployed+installed app and a TTY.

## Layer 1 — Static checks

```bash
forge lint            # manifest + handler wiring
forge lint --fix      # auto-fix what it can
```

## Layer 2 — Unit tests (mock the Forge boundary)

Forge resolvers and functions are plain JS/TS. Keep the logic in an exported function and mock `@forge/api`.

```javascript
// src/issues.js
import api, { route } from '@forge/api';

export async function getIssue(key) {
  const res = await api.asUser().requestJira(route`/rest/api/3/issue/${key}`);
  if (!res.ok) throw new Error(`Jira responded ${res.status}`);
  return res.json();
}
```

```javascript
// src/issues.test.js  (jest)
import api from '@forge/api';
import { getIssue } from './issues';

jest.mock('@forge/api', () => ({
  __esModule: true,
  default: { asUser: jest.fn() },
  route: (strings, ...vals) => strings.reduce((a, s, i) => a + s + (vals[i] ?? ''), ''),
}));

test('getIssue requests Jira as the user and returns the body', async () => {
  const json = jest.fn().mockResolvedValue({ key: 'TEST-1' });
  api.asUser.mockReturnValue({ requestJira: jest.fn().mockResolvedValue({ ok: true, json }) });

  await expect(getIssue('TEST-1')).resolves.toEqual({ key: 'TEST-1' });
  expect(api.asUser).toHaveBeenCalled();
});

test('getIssue throws on a non-ok response', async () => {
  api.asUser.mockReturnValue({ requestJira: jest.fn().mockResolvedValue({ ok: false, status: 404 }) });
  await expect(getIssue('NOPE-1')).rejects.toThrow('Jira responded 404');
});
```

### Mock cheat-sheet

```javascript
// @forge/api (backend)
jest.mock('@forge/api', () => ({
  __esModule: true,
  default: { asUser: jest.fn(), asApp: jest.fn() },
  route: (s, ...v) => s.reduce((a, x, i) => a + x + (v[i] ?? ''), ''),
  storage: { get: jest.fn(), set: jest.fn() },
}));

// @forge/kvs (storage)
jest.mock('@forge/kvs', () => ({ kvs: { get: jest.fn(), set: jest.fn(), delete: jest.fn() } }));

// @forge/bridge (Custom UI frontend)
jest.mock('@forge/bridge', () => ({
  invoke: jest.fn(),
  view: { getContext: jest.fn() },
  requestJira: jest.fn(),
}));
```

### Rovo action handlers

A Rovo action handler receives the agent-extracted inputs as its first argument (the invocation `context`, including the user `accountId`, is the second) — test it like any function:

```javascript
import { fetchRisks } from './index';
test('fetchRisks reads the projectKey input', async () => {
  const result = await fetchRisks({ projectKey: 'ABC' });
  expect(result).toBeDefined();
});
```

## Layer 3 — Live testing with `forge tunnel`

`forge tunnel` connects your local code to the app installed in the **development** environment, with real-time logs and fast turnaround (no redeploy per change). It runs `forge lint` and bundles first.

```bash
forge deploy -e development
forge install -e development --site <site> --product <jira|confluence>
forge tunnel                       # then exercise the app on the site
forge tunnel -d -f index.<exportName>   # breakpoint debugging (IntelliJ/VS Code)
```

`forge tunnel` must be run by the user in their own terminal (it needs a TTY).

## Layer 4 — Frontend and end-to-end

- **Custom UI**: render React components with `@testing-library/react`, mocking `@forge/bridge` `invoke` and `view.getContext`.
- **UI Kit**: test the resolver/logic in unit tests; verify rendering via `forge tunnel`.
- **E2E**: deploy + install on a test site, then drive the real UI with Playwright (or `forge tunnel` for live manual checks). Inspect runtime behavior with `forge logs -e development --limit 100`.

## CI integration

```yaml
# .github/workflows — run unit tests + lint on PRs
- run: npm ci
- run: npx forge lint
- run: npm test       # jest / node --test
```

Keep unit tests in CI (no Atlassian credentials needed — the Forge boundary is mocked). `forge tunnel`/install/e2e against a real site stay out of unmanned CI.

## Example triggers

- "Write unit tests for my Forge resolver"
- "How do I mock @forge/api in jest?"
- "Set up forge tunnel to test my app live"
- "Add a test job to my Forge app's CI"
- "How do I test a Rovo action handler?"

## Further reading

- [Tunneling](https://developer.atlassian.com/platform/forge/tunneling/)
- [forge tunnel CLI reference](https://developer.atlassian.com/platform/forge/cli-reference/tunnel/)
- [forge lint CLI reference](https://developer.atlassian.com/platform/forge/cli-reference/lint/)
