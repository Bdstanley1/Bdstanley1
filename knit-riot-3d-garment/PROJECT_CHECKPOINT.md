# Knit Riot / 3D Garment — Project Checkpoint

Updated 2026-10-01 UTC (September 30 in the owner's time zone).

## Release and deployment state

**PUBLIC PRODUCTION RELEASE: HOLD.** Overall lifelike appearance and physical garment fit have not passed. The old v09b male/cylinder service is not an approved release.

Existing Render workspace: `tea-dastcbd9fdbs73f0nrpg`; staging service: `srv-daudsoegekts73e2u1d0`; URL: https://knit-riot-studio-development.onrender.com. Preserved old v09b: `srv-datindfavr4c73dn25g0`.

At this checkpoint, live staging remains deploy `dep-dauq3hs9v7es73ahg1c0`, with old app SHA-256 `f70251a7a078a6e532ea80e3ab97374fa839bda9a79c3ff781dcc7ddf79f7901`. The newly validated GitHub candidate below has **not yet been deployed**. Check PROJECT_HANDOFF.json and Render live status for subsequent updates.

## Durable implementation, not a TODO-only repository

The owner authorized this public repository as the project repository. Root profile README and unrelated files are preserved.

The complete original staging source, generated application and source environment values have been recovered into `recovered/2026-09-30/`. Original snapshot SHA-256: `141fe99b2fa7dfddd46469da2b00a50d7767be31741ad32dd9c3156c47f9b0bb`. Verified synthetic body, skin, hair, HDR environment and Three.js dependencies are committed under `fixtures/runtime/`, including license attribution and checksum manifests. No real customer data was imported.

The upstream MakeHuman/Anny asset commit remains `d6fc027ced5c17b6b0775dee944096ade7a9ef80`. This is distinct from the project's current GitHub code commit. The anatomical adult female fixture has 13,380 source vertices, 26,756 body triangles and 163 native bones. Garment, body and accessories share weighted skinning.

The active build is `tools/build_runtime.py`, using the immutable baseline plus exact-once patches. It does not need a live staging fetch or expiring artifact. `tools/render_build.py` is the guarded Render publication path; `deployment/render_bootstrap.py` retrieves a pinned authorized project commit. A failed candidate test must leave the previous live deployment intact.

## Implemented repairs

`patches/refine.js` welds source-vertex copies, smooths the front garment surface independently of the body and constructs a continuous front envelope. `patches/mask.js` matches the clothing cuts and retains skin near boundaries. Actual front/detail/hand-on-hip renders show the earlier triangular shoulder breakthrough and nipple-like vest peaks repaired in these inspected views. This is an artistic garment envelope, not a measured cloth simulation; its maximum tested depth adjustment is about 0.0850 m.

`patches/runtime.json` synchronizes programmatic camera presets with visible controls, surfaces GLB exporter failures with button recovery, and embeds relevant asset credits and validation limits into exported GLB metadata.

The face, eyes, hair edges/materials and shoe proxies remain below the lifelike-reference requirement. Shoulder bindings, hands, garment boundaries and every pose still require continued visual review and refinement. Do not describe this as photorealism or a completed fitting room.

## Verified completed QA

Latest full successful workflow: `36799792982`, tested project commit `ab0a34b4b0d4d35359b2c681b3c38cb3a8785562`.

Assembled candidate app SHA-256: `2f244c54639dd84c0efe7417554d803f315ef5f0e5541ec8ec8c3e818a867218`.

Actual tool versions: Playwright 1.63.0; Pillow 12.3.0; software-rendered Chromium 153.0.8010.12. Python syntax checks and numerical garment invariants passed. Source body, topology, skin indices and weights were preserved; welded garment vertices remain coincident.

The browser suite completed without JavaScript/test/capture errors. It exercised all implemented button values; minimum/maximum/default range-state checks; orbit, wheel zoom and CDP-emulated pinch; geometry reset; seven emulated viewport sizes and eleven dock/layout states; essential body-load failure and optional exporter-load failure recovery.

All **420** size-label/color/pose/view selection combinations produced archived actual PNG frames. All **31** appearance cases produced actual PNG frames and cover all **284** pairs across skin, hair color, hairstyle, hair length, footwear, pose and view. Every frame was checksum-verified and checked for nonuniform pixels. Appearance coverage is pairwise, not the full Cartesian product. Pixel nonuniformity does not establish correct appearance. Size labels and bust/waist/hip controls remain comparison-only, not measured geometric fitting controls.

GLB export/reload succeeded with 18 visible skinned meshes. A comparison of 58,961 deformed world-space vertices found maximum roundtrip deviation `1.6971415172588268e-06` m. Actual reloaded front/side/back/detail renders are retained. This is serialization agreement, not scan or garment-fit accuracy.

`validation/latest/` durably contains raw results, evidence hashes, representative full-size actual renders, lossless atlases of all 420 selection-grid frames and all 31 pairwise-appearance frames, and PROVENANCE.json. QA is not confined to expiring Actions artifacts. Physical iPhone/Android/Mac/PC devices were **not tested**.

## Required next work, without scope reduction

Deploy the exact tested candidate to the existing staging service and verify the delivered app checksum and actual Render build results. Then continue correcting lifelike female appearance, eyes, hair, hands, shoe geometry, garment edges/body clipping and attachment throughout poses. Preserve every authorized appearance choice, 360 orbit, presets, zoom, reliable reset, compact status and non-overlapping phone/desktop controls.

Finish measurement-matched body geometry; real garment-size grading/ease visualization; provenance-backed material/cloth testing and distinction between proxy and actual-garment validation; safe customer-photo/import/profile handling; reusable personalized models across catalog browsing; and Shopify handoff/integration when specifically authorized access is genuinely available.

No purchases, new paid tiers/assets, unrelated account changes, production-store writes or real customer-photo transmission/publication. Continue all independent implementation before escalating a genuine external blocker. Full autonomous continuity instructions are in AGENTS.md.
