---
name: forge-marketplace
description: >
  Guides publishing and distributing Atlassian Forge apps: promoting from development to staging and
  production, configuring distribution, listing on the Atlassian Marketplace, app versioning and
  scope-change consent, licensing (free and paid-via-Atlassian), and pre-publish readiness. Use when
  the user wants to publish, distribute, share, or list a Forge app, promote an app to production, cut
  a new app version, set up paid/licensed apps, or prepare for Marketplace approval. Do not use for
  creating or dev-deploying an app (use forge-app-builder), deep security audits (use
  forge-security-review), or cost tuning (use forge-cost-optimizer).
license: Apache-2.0
labels:
  - forge
  - marketplace
  - distribution
  - publishing
  - atlassian
maintainer: atlassian-developer
namespace: cloud
---

# Forge Marketplace

Take a working Forge app from the development environment to **production**, then **distribute** it — privately or via the **Atlassian Marketplace**. This skill is the release/distribution lane; it hands deep security and cost work to the specialist skills.

## Boundaries

Use this skill for:

- Promoting an app to **staging** / **production** environments.
- Configuring **distribution** (private install vs. shared vs. Marketplace listing).
- Creating a **Marketplace listing** and cutting **app versions**.
- **Scope/permission changes** and the admin consent they trigger.
- **Licensing** (free or paid via Atlassian) and license checks.
- Pre-publish **readiness** and Marketplace approval preparation.

Use another skill when the primary intent is:

- Creating or dev-deploying an app, module choice, first `forge deploy` → **forge-app-builder**.
- Deep security audit / SAST / exploitability / CVSS → **forge-security-review**.
- Reducing invocations, storage, or memory cost → **forge-cost-optimizer**.
- Broad pre-release readiness review → **forge-app-review**.
- A specific deploy/install failure or error → **forge-debugger**.

## Critical Rules

1. **Production is a separate environment** — `development` is for building; ship to users via `staging`/`production`. Test in `staging` before `production`.
2. **New scopes require admin consent** — adding permissions in a new version forces installed sites to re-consent/upgrade. Request the **minimum** permissions and call out scope changes in release notes.
3. **Don't list before it's ready** — Marketplace apps undergo Atlassian review (security, data residency, branding). Run `forge-security-review` and `forge-app-review` first.
4. **Never ship secrets** — no hardcoded credentials/tokens; use Forge environment variables. Confirm with `forge-security-review`.
5. **A listed app is a support commitment** — version, changelog, and support expectations apply once published.

## Workflow

### Step 0: Pre-publish readiness

- `forge lint` is clean; the app deploys and installs in `development`.
- Run **forge-app-review** (release readiness) and **forge-security-review** (security/approval requirements). Address blockers first.
- Confirm app metadata: name, description, icon, support details.

### Step 1: Promote to staging / production

Forge separates environments; promote the same code to production:

```bash
forge deploy -e staging
forge install -e staging --site <site> --product <jira|confluence>
# validate in staging, then:
forge deploy -e production
forge install -e production --site <site> --product <jira|confluence>
```

See [Promote an app to staging or production](https://developer.atlassian.com/platform/forge/staging-and-production-apps/) for environment restrictions and requesting the minimum set of permissions from users.

### Step 2: Choose a distribution model

Forge apps are **private by default** (installable only by the developer). To reach users, either share the app for direct install or list it publicly on the Marketplace. See [Distribute your apps](https://developer.atlassian.com/platform/forge/distribute-your-apps/) for the current distribution controls and eligibility (for example, Runs on Atlassian / egress and data-residency implications).

### Step 3: Create the Marketplace listing

List the production app through the [Atlassian Developer Console](https://developer.atlassian.com/console/) → your app → Distribution / Marketplace:

- Listing details: summary, description, categories, screenshots, support and privacy URLs.
- Submit the app version for Atlassian review/approval.

### Step 4: Version and ship updates

- Cutting a new version: deploy the updated code to production, then publish the new version on the listing.
- **Major version**: created for consent-impacting changes such as adding scopes. Privilege-escalating scope changes require admin consent on upgrade (some non-escalating major upgrades can be applied without it). Communicate scope changes in release notes.
- **Minor version**: backward-compatible changes that don't add scopes.

### Step 5: Licensing (optional, for paid apps)

- Forge supports free apps and **paid-via-Atlassian** licensing. Configure pricing on the Marketplace listing.
- Gate features by reading the installation's license state at runtime (license context). Handle the trial/unlicensed states gracefully.
- See the Marketplace licensing documentation for the current API and pricing-model options.

### Step 6: Post-publish

- Monitor `forge logs -e production --site <site>` and app analytics.
- For incidents, hand off to **forge-debugger**.
- Keep scopes minimal across versions to avoid repeated admin re-consent.

## Pre-publish readiness checklist

- [ ] `forge lint` clean; deploy + install verified in `staging`.
- [ ] `forge-security-review` passed (no hardcoded secrets, least-privilege scopes, safe egress).
- [ ] `forge-app-review` passed (manifest/module wiring, runtime, dependencies).
- [ ] Scopes are minimal; any scope change is flagged as a major version.
- [ ] Listing assets ready (name, description, icon, screenshots, support/privacy URLs).
- [ ] Data residency / egress reviewed for Marketplace eligibility.
- [ ] Licensing/pricing decided (free vs paid) and the unlicensed state handled.

## Example triggers

- "Publish my Forge app to the Marketplace"
- "Promote this app to production"
- "Cut a new version — I added a scope, what do users need to do?"
- "Make this a paid app"
- "What do I need before listing on the Marketplace?"

## Further reading

- [Promote an app to staging or production](https://developer.atlassian.com/platform/forge/staging-and-production-apps/)
- [Distribute your apps](https://developer.atlassian.com/platform/forge/distribute-your-apps/)
- [Atlassian Developer Console](https://developer.atlassian.com/console/)
- [Forge platform documentation](https://developer.atlassian.com/platform/forge/)
