# Knit Riot / 3D Garment — Reconciled Project Checkpoint

Updated 2026-10-03 UTC.

## Release state
**PUBLIC PRODUCTION RELEASE: HOLD.** Overall human realism, physical garment fit, measurement reconstruction, actual-garment validation, privacy/customer-data gates and real-device validation are not complete.

## Canonical tested source
The canonical product source selected by reconciliation is:

- Project source commit: `2a981f207c2643f993b76fec6f24ec20d87d93f8`
- Assembled app SHA-256: `a165ab2eb31dfff89ed2cedfcfe8af02b5954f165b66a1d33ace584bb5865afc`
- Actual-render workflow: `37085768033` — **success**
- Durable evidence commit: `fb1c1e261083d646163a9ac1b72c05a1abd99246`
- Rendered-review artifact SHA-256: `27837701d22747ac3a5c55d86dce93850d8101880b4b18afb1917cecf796a5a2`
- Pinned-source artifact SHA-256: `9d429992cb13f491dcd2c78484b327f69fd8b8825e41c7454b0a5da178e43af8`

The artifact digest was independently recomputed after download and matched GitHub.

### Actual QA at the canonical source
- 420 actual selection-grid renders: exhaustive across the existing 7 size labels × 3 colors × 5 poses × 4 views.
- 31 appearance renders covering all 284 value pairs across the listed appearance factors: pairwise, not exhaustive Cartesian coverage.
- 15 garment binding closeups: exhaustive across 5 implemented poses × front/side/back presets.
- Footwear close-up and occlusion coverage remains preserved from the current suite, including barefoot negative controls.
- GLB export/reload: 21 meshes, 60,353 deformed vertices compared, maximum numerical world-space deviation `1.6971415172588268e-06 m`.
- JavaScript/test errors: none.
- Capture errors: none.
- Software-rendered Chromium only; physical iPhone/Android/Mac/PC hardware was not validated.

Actual image inspection of the canonical binding atlas and front/side/back renders found the specific residual inner-shoulder binding tab targeted by the final source repair no longer apparent in the reviewed views. This is a local visual milestone only; the avatar and garment still do **not** pass the overall realism gate.

## Reconciliation result
The overlapping chats produced coordination drift, but Git history remained linear. The reconciliation audit therefore did **not** roll back merely to an older timestamp. Instead it selected the newest cumulative source commit that:
1. includes the later repairs,
2. passed the current full actual-render regression,
3. has checksum-verifiable durable evidence, and
4. was visually inspected for the repair area.

Evidence-only bot commits above the canonical product source are not treated as product source. Failed/intermediate experiments remain historical evidence and are not canonical merely because they are newer.

The single-writer protocol is now defined in `COORDINATION_LOCK.md`. The active writer is the session holding the bounded lease in `PROJECT_HANDOFF.json`; chat titles alone are not authority.

## Current staging state before canonical publication
Existing staging service: `srv-daudsoegekts73e2u1d0` in Render workspace `tea-dastcbd9fdbs73f0nrpg`.

Current live deploy observed during reconciliation:
- Deploy: `dep-db0461s9v7es739rraog`
- Project commit from Render build/app logs: `3ed5ad8c1041af0e64a2a055e2fcd81fa31df2de`
- Delivered app SHA-256 from logs: `b548985c10f806ca66fbce1df8a0382d85032a9fec27b479bb44d26244acf54c`

That live staging build passed its own browser suite, but it is **behind the reconciled canonical source**. It must not be described as the canonical delivered build until exact `2a981f… / a165ab2…` publication and independent HTTPS delivery verification complete.

Preserve old v09b service `srv-datindfavr4c73dn25g0`; it fails the female-avatar requirement and is not an approved release. Preserve the root profile README and unrelated files.

## Current implemented direction
The canonical source contains the cumulative shoe reconstruction, forefoot occlusion QA, intact upper-body/armhole repairs, hair-material refinements, and the later vest shoulder/binding finishing changes. The full rendered suite remains functional.

Known limits remain explicit:
- Overall face/eyes/skin/hair/hands/footwear realism is not approved.
- Armhole/shoulder/binding cleanup is improved but does not establish overall garment realism or physical fit.
- Size/bust/waist/hips are not yet completed and validated geometric reconstruction controls.
- GLB numerical agreement is serialization agreement, not fit/measurement validation.
- Synthetic reference images are not measured body or garment ground truth.

## Next autonomous work
1. Publish exact canonical `2a981f…` / `a165ab2…` to the **existing** Render staging service using the guarded build path; do not create another service.
2. Independently verify the exact delivered app, project commit, assets, QA evidence and source archive over HTTPS.
3. Continue actual-render inspection and repair of face/eyes/skin/hair/hands/footwear and pose-specific garment boundaries/clipping.
4. Implement and actual-test measurement-matched body geometry.
5. Implement actual garment grading/ease visualization and provenance-backed cloth/material tests, clearly separating artistic/proxy simulation from validation against the real garment.
6. Complete safe customer profile/photo architecture without transmitting real customer data, reusable personalized catalog model, and specifically authorized Shopify handoff.

## Safety / autonomy
No purchases, paid tiers/subscriptions/assets, new services, unrelated account changes, production-store writes, credentials/customer data in public repo/logs/artifacts, or customer-photo transmission/publication without explicit authorization/consent.

The hourly task `6abce881c74c8191b819dffcb2e54841` remains paused until the canonical staging delivery is independently verified. When re-enabled, it is a recovery/watchdog mechanism subordinate to any active interactive lease.
