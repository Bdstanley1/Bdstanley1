# Knit Riot / 3D Garment — Project Checkpoint

This directory is the durable project repository authorized by the owner on 2026-09-30.

## Existing staging
- Render workspace: `tea-dastcbd9fdbs73f0nrpg`
- Staging service: `srv-daudsoegekts73e2u1d0`
- Staging URL: `https://knit-riot-studio-development.onrender.com`
- Preserved old v09b service: `srv-datindfavr4c73dn25g0` (not an approved release; fails female-avatar requirement)
- Upstream asset source pinned to NAVER/anny commit `d6fc027ced5c17b6b0775dee944096ade7a9ef80`

## Current implementation state
- Anatomical adult female MakeHuman mesh: 13,380 vertices, 26,756 triangles, 163 bones.
- Body, vest, leggings, shoes and buttons use weighted skinning.
- Licensed Elvaerwyn Ashley May hair is in the current corrective build.
- Phone controls use a separate grid row; desktop controls are docked.
- Playwright Chromium QA runs during Render builds and archives `/qa/results.json` plus rendered stills.

## Current gate
PUBLIC RELEASE: **HOLD**.

Latest recorded QA reached individual control tests but stopped on a screenshot timeout before the intended 420-render sweep. Visual realism has not passed. Known defects include garment/shoulder/armhole behavior and insufficient realism. Physical garment fit has not been validated.

## Required continuation
Repair visual artifacts first; verify actual renders; then finish measurement-matched body geometry, real garment size/grade/ease visualization, provenance-backed material/cloth validation, safe customer profile/photo handling, reusable model, and Shopify handoff when authorized access exists.

Never claim photorealism, physical fit/comfort accuracy, exhaustive hardware compatibility, or project completion without corresponding evidence.
