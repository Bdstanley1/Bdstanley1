# Knit Riot coordination lock

Effective 2026-10-03 UTC by owner request.

## Authority
The **Continue Knit Riot Development** project/chat is the sole implementation coordinator after reconciliation. This chat/audit context must not independently mutate product source, Render staging, QA expectations, or release state.

## Current reconciliation state
- Scheduled autonomous task `6abce881c74c8191b819dffcb2e54841` is PAUSED during reconciliation.
- GitHub main history is linear/recoverable, but PROJECT_HANDOFF.json and PROJECT_CHECKPOINT.md are stale relative to later source and Render staging.
- A workflow for commit `c700e4f1efe4d7c05d768255a1264d136165689a` was already running when Stop was requested; treat its result as audit evidence only, not authorization for further implementation.
- Current observed staging deploy during audit: `dep-db0461s9v7es739rraog`, live since 2026-10-02T23:59:16Z. Exact project commit/app bytes must be independently reconciled before continuation.
- Production release remains HOLD.

## Mandatory single-writer protocol
1. Before any future source or staging mutation, read this file, AGENTS.md, PROJECT_HANDOFF.json and PROJECT_CHECKPOINT.md.
2. Only the Continue Knit Riot Development coordinator may acquire the implementation lease and mutate source/staging.
3. Other chats may research, review, or provide owner feedback, but must not independently implement while this lock is active.
4. Update PROJECT_HANDOFF.json and PROJECT_CHECKPOINT.md to the reconciled canonical commit/deploy before resuming ordinary implementation.
5. Verify the canonical GitHub commit with actual rendered QA and verify the exact Render-delivered commit/app/assets separately.
6. Do not infer canonical state from the newest commit alone; failed/intermediate experiments remain history, not automatically accepted product state.
7. Keep the autonomous hourly task paused until the Continue Knit Riot Development coordinator explicitly completes reconciliation and records the canonical state.
8. Once reconciliation is complete, that coordinator may replace this temporary lock with a durable single-writer/lease rule, then resume autonomous implementation.

No production-store writes, purchases, new services, customer-data transmission, or relaxation of existing QA/safety gates.
