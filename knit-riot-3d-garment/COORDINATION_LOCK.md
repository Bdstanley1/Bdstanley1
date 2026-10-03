# Knit Riot single-writer coordination protocol

Effective 2026-10-03 UTC by owner instruction.

## Authority
The project uses a **single active implementation writer**. The writer is the interactive session holding the unexpired lease recorded in `PROJECT_HANDOFF.json`. All other chats/automations are audit/review-only while that lease is active.

The owner has now explicitly authorized autonomous continuation in the current interactive control session. This session may reconcile state, acquire the lease, update source/staging, run QA, inspect rendered evidence, repair defects, and advance according to `AGENTS.md`.

Chat titles are not themselves authority. A later explicit owner transfer supersedes an older chat-name assignment. This avoids the previous ambiguity between “Continue Knit Riot” and “Continue Knit Riot Development”.

## Reconciled source rule
- Canonical product source is selected from an **actual tested source commit**, not simply the newest Git commit.
- Evidence-only bot commits may sit above the canonical source commit without changing product source.
- Failed/intermediate experiments remain history and are not canonical merely because they are newer.
- Before staging publication, the canonical source commit, assembled app SHA-256, successful actual-render workflow, and visually inspected evidence must agree.
- Staging must then be independently checked for exact delivered project commit/app/assets/QA.

## Lease protocol
1. Read this file, `AGENTS.md`, `PROJECT_HANDOFF.json`, and `PROJECT_CHECKPOINT.md` before mutation.
2. Do not mutate source or staging if another unexpired lease is present.
3. Acquire/renew a bounded lease in `PROJECT_HANDOFF.json` before source/staging mutation.
4. The hourly recovery/watchdog automation must defer to an active interactive lease.
5. At session end, checkpoint tested source, evidence, live staging state, unresolved defects, and next actionable work.
6. Production remains HOLD until all applicable visual, functional, privacy, provenance, physical-garment and hardware gates pass.

## Preserved constraints
Use only existing Render workspace `tea-dastcbd9fdbs73f0nrpg` / service `srv-daudsoegekts73e2u1d0`. Preserve old v09b `srv-datindfavr4c73dn25g0`, the root profile README, unrelated files, and the immutable recovered baseline. No purchases, paid tiers/assets, new services, production-store writes, credentials/customer data in public source/logs/artifacts, or customer-photo transmission/publication without explicit authorization/consent.
