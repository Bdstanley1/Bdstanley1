# Knit Riot / 3D Garment — Project Checkpoint

Updated 2026-10-03 UTC.

## Release state
**PUBLIC PRODUCTION RELEASE: HOLD.** Overall human realism, physical garment fit, measurement reconstruction, actual-garment validation, privacy/customer-data gates, and physical-device validation remain incomplete.

## Canonical tested product source
The newest cumulative product source that has passed the current actual-render regression and visual review for its change area is:

- Project source commit: `3cc585e40dacf1bfdd7470688fc95464e818ca18`
- Assembled app SHA-256: `46f273b770cc5102e1b78c4bb51e67f0906fd0c8a7086382cc059701bc507dbc`
- Actual-render workflow: `37089473942` — **success**
- Durable evidence commit: `7d0861324a4d659a3c89de277a36ccfaa8f36426`
- Rendered-review artifact: `11262112796`
- Rendered-review artifact SHA-256: `ce92b930c5176953113fefc82a3529e42c3b3a8b1810f31e0307bd86b0c0ea05`
- Pinned-source artifact: `11261938152`
- Pinned-source artifact SHA-256: `b4136f86a61860ccd2412038922085254ec2602f76aafcf3e9826b990514049d`

The downloaded rendered-review artifact digest was independently recomputed and matched GitHub.

### Executed QA on the canonical source
- 420 actual selection-grid renders: exhaustive across the existing 7 size labels × 3 garment colors × 5 poses × 4 views.
- 31 appearance cases covering all 284 value pairs across the listed appearance factors: pairwise, not exhaustive Cartesian coverage.
- 108 dedicated hair closeups: exhaustive across 6 hair colors × 3 implemented styles × 3 length boundary/default values × front/side views.
- 40 footwear normal closeups: exhaustive across 2 footwear states × 5 poses × 4 camera directions.
- 40 footwear occlusion diagnostics: exhaustive across the same 2 × 5 × 4 grid, including barefoot negative controls.
- 15 garment binding closeups: exhaustive across 5 poses × front/side/back.
- GLB export/reload/rerender: 21 meshes and 60,353 deformed vertices compared; maximum numerical world-space deviation `1.6971415172588268e-06 m`.
- JavaScript/test errors: none.
- Capture errors: none.
- Software-rendered Chromium only; no physical iPhone/Android/Mac/PC hardware validation.

GLB numerical agreement is serialization agreement, not measurement accuracy or physical fit.

## Ashley May hair-normal integration
The licensed Ashley May normal map is retained in the tested source through checksum-verified fixture provenance only.

- Pinned source archive SHA-256: `c681e5efd37df4007a52253a8d071aedbfe3b614f199d8dae4ae76d5bd7d95c9`
- Original member SHA-256: `871a5acddb9c57a6f116d0603d80fa534a649c6b1af659ca39fb972dd5d18d60`
- The original member contains one corrupt ancillary iCCP CRC while its IDAT is valid.
- Deterministic repair removes only the bad iCCP chunk, preserves IDAT byte-for-byte, and produces runtime fixture SHA-256 `3fbca1cc964a29eec0eb24f6b8c4612b7661bedaca61db597b8a813973786cb0`.
- Source attribution remains Elvaerwyn / CC-BY. No measured hair-optics claim is inferred from the asset.

Actual before/after inspection found the normal-map effect modest and localized to the hair region in the representative desktop-detail comparison, with no observed face/skin/garment spillover there. The complete candidate hair atlas and native representative front/side frames were inspected. Hair geometry still reads as coarse card/ribbon/clump geometry, especially at curls and silhouette transitions. **Overall hair/human realism remains NOT APPROVED.**

## Staging state
Existing Render staging service: `srv-daudsoegekts73e2u1d0` in workspace `tea-dastcbd9fdbs73f0nrpg`.

At this checkpoint the live deploy remains `dep-db0653ugekts738b8140`, independently verified to serve the previous tested source:
- Delivered project commit: `2a981f207c2643f993b76fec6f24ec20d87d93f8`
- Delivered app SHA-256: `a165ab2eb31dfff89ed2cedfcfe8af02b5954f165b66a1d33ace584bb5865afc`
- Delivery verification workflow: `37088981741`

The newer canonical tested source `3cc585e...` has **not yet been claimed live**. Publication must use the guarded build entry point, and exact delivery must be independently re-verified before staging is checkpointed as updated. An environment merge triggers the Render deploy; do not trigger a duplicate.

Preserve old v09b service `srv-datindfavr4c73dn25g0`; it is not an approved release. Preserve the repository root profile README, unrelated files, and immutable recovered baseline.

## Known defects / next autonomous work
1. Publish and independently delivery-verify exact `3cc585e...` / `46f273b...` on the existing staging service.
2. Continue actual-rendered hair geometry/silhouette repair; the normal map does not solve the dominant card/clump defect.
3. Continue face, eyes, skin, hands, footwear and pose-specific garment boundary/clipping realism repair.
4. Implement and actual-test measurement-matched body geometry; current size/bust/waist/hips are not validated geometric reconstruction controls.
5. Implement actual garment grading/ease visualization and provenance-backed material/cloth testing, explicitly separating artistic/proxy simulation from validation against the physical garment.
6. Complete safe customer profile/photo architecture without transmitting real customer data, reusable personalized catalog model, and specifically authorized Shopify handoff.

## Coordination / safety
The single writer is the session holding the unexpired bounded lease in `PROJECT_HANDOFF.json`. The hourly recovery/watchdog remains subordinate to that lease.

No purchases, paid tiers/subscriptions/assets, new services, unrelated account changes, production-store writes, credentials/customer data in public source/logs/artifacts, or customer-photo transmission/publication without explicit authorization/consent.
