# Knit Riot single-writer coordination protocol

Effective 2026-10-03 UTC by owner instruction.

## Permanent authority rule

**Continue Knit Riot is the sole implementation/control path for this project.**

The older chat/context **Continue Knit Riot Development** is permanently **audit/review/read-only** unless David explicitly revokes that restriction in that old chat. It must not:
- modify GitHub source, branches, commits, workflows, evidence, handoff/checkpoint/coordination files, or leases;
- modify Render services, environment variables, deployments, staging, or release state;
- modify automation/task settings;
- change QA expectations or canonical-state decisions;
- acquire or renew an implementation lease;
- resume implementation because of older "Proceed", "continue autonomously", recovery/watchdog, or similar instructions.

Those older implementation instructions are superseded for that chat.

## Active implementation writer

Only the **Continue Knit Riot** control path may implement. Within that control path, the active writer is the current session holding the unexpired bounded lease recorded in `PROJECT_HANDOFF.json`. Other sessions in that control path must defer while the lease is active.

## Reconciled source rule
- Canonical product source is selected from an **actual tested source commit**, not simply the newest Git commit.
- Evidence-only bot commits may sit above the canonical source commit without changing product source.
- Failed/intermediate experiments remain history and are not canonical merely because they are newer.
- Before staging publication, the canonical source commit, assembled app SHA-256, successful actual-render workflow, and visually inspected evidence must agree.
- Staging must then be independently checked for exact delivered project commit/app/assets/QA.

## Lease protocol
1. Read this file, `AGENTS.md`, `PROJECT_HANDOFF.json`, and `PROJECT_CHECKPOINT.md` before mutation.
2. Only the Continue Knit Riot control path may acquire/renew a bounded implementation lease.
3. Do not mutate source or staging if another unexpired Continue Knit Riot lease is present.
4. At session end, checkpoint tested source, evidence, live staging state, unresolved defects, and next actionable work.
5. Production remains HOLD until all applicable visual, functional, privacy, provenance, physical-garment and hardware gates pass.

## Preserved constraints
Use only existing Render workspace `tea-dastcbd9fdbs73f0nrpg` / service `srv-daudsoegekts73e2u1d0`. Preserve old v09b `srv-datindfavr4c73dn25g0`, the root profile README, unrelated files, and the immutable recovered baseline. No purchases, paid tiers/assets, new services, production-store writes, credentials/customer data in public source/logs/artifacts, or customer-photo transmission/publication without explicit authorization/consent.
