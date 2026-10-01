# Knit Riot / 3D Garment Virtual Fitting Room

**Development only. Production release is on HOLD. Visual realism and physical garment fit are not approved.**

This is the owner's authorized public project namespace. The repository's root profile README is preserved. No real customer photos, measurements, profiles or credentials belong in this repository.

## Working implementation

The project contains an anatomical adult female MakeHuman fixture, its native weighted rig, a skinned vest, leggings, footwear proxies, licensed hair and skin, orbit/camera controls and a responsive controls dock. The vest surface is refined independently of the body, and covered-body masking preserves boundary skin. The current face, hair and footwear still require realism work.

`recovered/2026-09-30/` is the immutable prior staging source. `fixtures/runtime/` contains the checksum-verified synthetic fixture, runtime dependencies and attribution. `patches/` contains the actual current repairs. `tools/build_runtime.py` applies each repair exactly once to the pristine baseline and builds the application without depending on staging or expiring download links.

## Build locally

From the repository root, with Python and Node installed:

```sh
python knit-riot-3d-garment/tools/build_runtime.py --output knit-riot-3d-garment/public
python -m http.server 8000 --directory knit-riot-3d-garment/public
```

Open `http://localhost:8000`. The build verifies all fixture files before writing output and records the assembled app checksum in `BUILD_REPORT.json`. The portable `development-snapshot.zip` contains the actual generated runtime, not a reference image.

## Run the actual regression

```sh
python -m pip install -r knit-riot-3d-garment/requirements-test.txt
python -m playwright install --with-deps chromium --only-shell
node knit-riot-3d-garment/tools/test_geometry.cjs
python knit-riot-3d-garment/tools/render_test.py
```

The GitHub Actions workflow runs these checks on a standard Ubuntu runner and preserves actual rendered outcomes. `validation/latest/PROVENANCE.json` identifies the tested commit, workflow run and app checksum. `results.json` describes what executed. The lossless render atlases preserve every sampled frame, and individual full-size views are retained for inspection.

Coverage includes all implemented button values; minimum, maximum and default range-state checks; orbit, zoom, emulated pinch and geometry reset; seven emulated viewport sizes and eleven dock/layout states; the full 420-case size-label/color/pose/view selection grid; 31 appearance cases covering all 284 value pairs across seven factors; essential-asset and exporter failure paths; and GLB export, reload, actual re-rendering and deformed world-vertex comparison. Coverage is not the full appearance Cartesian product, physical-device testing or physical garment validation. Size labels and bust/waist/hip inputs still do not implement measured grading/body reconstruction.

## Existing staging

The existing deployment is https://knit-riot-studio-development.onrender.com. Its live version must be checked independently of GitHub CI; a passed commit is not automatically a deployed commit. `tools/render_build.py` is a guarded deployment entry point: it requires a pinned project commit and expected app checksum, reruns actual browser tests and publishes only a passing candidate. Do not create another service or overwrite an old working service to make a correction.

See `PROJECT_CHECKPOINT.md`, `PROJECT_HANDOFF.json` when present, and `AGENTS.md` for continuity, remaining requirements and release gates. Asset attribution is retained in `fixtures/runtime/ATTRIBUTION.txt` and `asset-manifest.json`, with relevant credits also embedded in exported GLB metadata.
