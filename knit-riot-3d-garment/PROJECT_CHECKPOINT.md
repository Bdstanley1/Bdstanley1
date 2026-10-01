# Knit Riot / 3D Garment — Project Checkpoint

Updated 2026-10-01 UTC (September 30 in the owner's time zone).

## Current live implementation

**PUBLIC PRODUCTION RELEASE: HOLD.** Overall lifelike appearance and physical garment fit have not passed. This is a validated development milestone, not project completion.

The existing staging service `srv-daudsoegekts73e2u1d0` in Render workspace `tea-dastcbd9fdbs73f0nrpg` is live at https://knit-riot-studio-development.onrender.com.

- Live deploy: `dep-daurcmg473hc73cb9ljg`, live since `2026-10-01T01:30:02.659572Z`.
- Tested/deployed project code: `ab0a34b4b0d4d35359b2c681b3c38cb3a8785562`.
- Delivered app SHA-256: `2f244c54639dd84c0efe7417554d803f315ef5f0e5541ec8ec8c3e818a867218`.
- Independent HTTPS delivery verification: workflow `36801168765`, successful retry after the initial waiting deadline expired before the candidate became live. Assertions were not weakened.
- Delivered source archive: `/development-snapshot.zip`, 31,518,484 bytes; SHA-256 `ec8dfad72e31a13bed69a6057ca58d6972032ba144cb59bb0213104062f8ae0e`.

The previous staging deployment remains in Render history. Old v09b `srv-datindfavr4c73dn25g0` is preserved but fails the female-avatar requirement and is not an approved release. Root profile README is unchanged: blob `94740cd20916824e2058a62c8b6790d3943df143`.

## Durable source and reproducible build

The owner authorized the public `Bdstanley1/Bdstanley1` repository under `knit-riot-3d-garment/`. Complete original application/build source is retained immutably in `recovered/2026-09-30/`. Its original snapshot SHA-256 is `141fe99b2fa7dfddd46469da2b00a50d7767be31741ad32dd9c3156c47f9b0bb`.

The anatomical adult female fixture has 13,380 source vertices, 26,756 body triangles and 163 native bones. Body, vest, leggings, footwear proxies and buttons share weighted skinning. Licensed skin, Ashley May hair, studio environment and Three.js dependencies are committed and checksum-verified in `fixtures/runtime/`, with attribution. No real customer data was imported.

The upstream asset commit `d6fc027ced5c17b6b0775dee944096ade7a9ef80` is distinct from the current project code commit. Active assembly is `tools/build_runtime.py` plus exact-once `patches/`, not the old environment-variable patch chain. `deployment/render_bootstrap.py` is stored in Render BUILD_PY; it checks out a pinned KR_PROJECT_COMMIT. `tools/render_build.py` checks KR_EXPECTED_APP_SHA, reruns actual browser QA, then publishes only a passing candidate. Legacy environment source remains for rollback/provenance. An env update already triggers deployment; do not duplicate the trigger or create another service.

## Actual implemented repairs

The garment is refined independently of the body through source-vertex welding, front-surface smoothing and a continuous chest envelope. A coverage mask now matches clothing cuts and retains skin at boundaries. Inspected actual front/detail/hand-on-hip renders show the earlier triangular shoulder breakthrough and nipple-like vest peaks repaired. The maximum tested front-envelope depth adjustment is about 0.0850 m; this is artistic garment geometry, not measured cloth behavior.

Programmatic camera presets synchronize visible controls. Export errors are visible and restore the button. Exported GLBs include relevant asset credits and explicit non-validation metadata.

## Completed actual QA, with limits

GitHub workflow `36799792982` passed; the full suite also completed in the actual Render build without test or capture errors. Tool versions were Playwright 1.63.0, Pillow 12.3.0 and software-rendered Chromium 153.0.8010.12. Python syntax and numerical garment invariants passed; the original body, topology, skin indices and weights were preserved, and welded garment seams remained coincident.

The implemented button values, minimum/maximum/default range-state checks, orbit, wheel zoom, CDP pinch, geometry reset, essential body-load failure and optional exporter-load failure recovery passed. Eleven dock/layout states across seven emulated viewports had no panel/stage overlap or overflow.

All **420** size-label/color/pose/view selection combinations produced actual PNGs. **31** appearance renders cover all **284** value pairs across skin, hair color, hairstyle, length, footwear, pose and view. Every frame was checksum-verified and checked for nonuniform pixels. This is one exhaustive selection grid plus pairwise appearance coverage, not exhaustive overall state space or visual approval. Size labels and bust/waist/hips remain comparison inputs, not geometric fitting controls. Range-state checks must be strengthened when measurement-driven geometry is implemented.

GLB export/reload retained 18 skinned meshes. Comparison of 58,961 deformed world-space vertices found maximum numerical roundtrip deviation `1.6971415172588268e-06` m. Actual reloaded front/side/back/detail images are retained. This tests serialization, not body reconstruction or garment fit.

The independent delivery check verified the exact served app/commit, seven served asset files, QA results, actual Render screenshots and portable source archive. `validation/latest/` retains CI results, provenance, full-size views and lossless atlases of every rendered test frame. The staging-verification workflow maintains `validation/staging/` with actual delivered Render images and verification provenance. Source/evidence no longer depends only on temporary artifacts. Physical iPhone/Android/Mac/PC hardware was **not tested**.

## Next autonomous repairs and full remaining scope

The face, eyes, hair, hands and shoe proxies still fall below the lifelike-reference requirement. Continue neckline/armhole/hem/shoulder binding and body-clipping/attachment review across every pose. Actual Render screenshots also expose a zoom-glyph font fallback that CI screenshots did not; fix the glyph rendering without losing real zoom behavior.

The source hair material identifies the omitted normal map `hair/elvs_ashley_may_hair/80snormals.png` in the already identified hair02 CC-BY asset pack. This is a concrete next appearance-improvement lead, not an implemented fix. Verify source/checksums/attribution and compare actual renders.

Preserve every approved appearance choice, lifelike adult brunette female target, natural poses, genuine skinned 3D garment, 360 orbit, presets, zoom, reliable reset, compact status and separate non-overlapping phone/desktop controls. No male/T-pose/mannequin/cylinder/2D substitution; reference images are not measured ground truth.

Finish measurement-matched body geometry; real garment-size grading/ease; provenance-backed material/cloth testing distinguishing proxy simulation from actual-garment validation; safe customer-photo/import/profile handling; model reuse across catalog browsing; and specifically authorized Shopify handoff/integration. Do not infer pressure, comfort or physical fit from rendered appearance. Do independent engineering before escalating truly missing external evidence or authorization.

No purchases, paid tiers/assets, new services, unrelated account changes, production-store writes, credentials in source/logs, or real customer-photo transmission/publication without required authorization/consent. Preserve all approved scope.

The existing autonomous implementation task `6abce881c74c8191b819dffcb2e54841` is enabled hourly, next scheduled at `2026-10-01T02:32:42Z`, after the current bounded staging lease. Continue build → actual render/control tests → repair → retest → advance, with no routine approval questions. Notify only a meaningful new validated milestone, genuine external blocker or completion. AGENTS.md and PROJECT_HANDOFF.json contain the full continuation contract and exact state.
