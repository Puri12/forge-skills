# Forge Marketplace Skill

Guides **publishing and distributing** Atlassian Forge apps — promoting from development to production, configuring distribution, listing on the Atlassian Marketplace, app versioning, scope-change consent, and licensing.

This is the release/distribution lane. It picks up where **forge-app-builder** (dev create/deploy) leaves off, and routes deep checks to the specialist skills.

## Use For

- Promoting an app to **staging** / **production**
- Choosing a distribution model (private install vs. Marketplace listing)
- Creating a Marketplace listing and cutting app versions
- Scope/permission changes and the admin consent they trigger
- Licensing (free or paid-via-Atlassian) and pre-publish readiness

## Do Not Use For

- Creating or dev-deploying an app, module choice → **forge-app-builder**
- Deep security audit / SAST / CVSS → **forge-security-review**
- Cost/consumption tuning → **forge-cost-optimizer**
- A specific deploy/install failure → **forge-debugger**

## What It Covers

- **Environments** — `development` → `staging` → `production` promotion and restrictions.
- **Distribution** — private vs. shared vs. Marketplace; eligibility and data-residency implications.
- **Listing** — Atlassian Developer Console listing details and review/approval.
- **Versioning** — minor vs. major; major versions when scopes change (admins must re-consent).
- **Licensing** — free and paid-via-Atlassian; gating features on license state.
- **Readiness** — a pre-publish checklist with security and review handoffs.

## Example Prompts

```text
Promote my Forge app to production and list it on the Marketplace.
```

```text
I added a new scope — what version bump do I need and what do admins have to do?
```

```text
What's the checklist before I publish this app?
```

## Further Reading

- [Promote an app to staging or production](https://developer.atlassian.com/platform/forge/staging-and-production-apps/)
- [Distribute your apps](https://developer.atlassian.com/platform/forge/distribute-your-apps/)
- [Atlassian Developer Console](https://developer.atlassian.com/console/)

See [SKILL.md](SKILL.md) for the full workflow, rules, and readiness checklist.
