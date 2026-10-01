# Competitive R&D — Virtual Fitting / 3D Garment

Updated 2026-10-01. This is an engineering comparison, not evidence that vendor marketing claims are independently validated.

## Relevant product architectures

### Style.me
- Shopper creates an avatar from basic measurements and body-shape selections.
- Maps garment patterns/sizes to shopper measurements; supports avatar appearance personalization, mix-and-match/layering and e-commerce integration.
- Lesson: separate **body identity/profile**, **garment pattern/size data**, and **presentation/styling**. Our persistent personalized model and catalog reuse should follow this separation.

### Reactive Reality / PICTOFiT
- Explicit asset pipeline: avatar + garment(s) + scene + optional animation.
- Content Service can generate garments from mannequin images, 3D scans or CAD; avatar assets can come from model photos.
- Supports 2D, parallax and true 3D dressing-room modes, size recommendation/fit visualization, layered outfits and Shopify integration.
- Web integration uses strongly versioned components and runtime asset-type checks.
- Lesson: make asset provenance/type first-class metadata; do not pretend every source supports the same fidelity. Build a garment ingestion layer with explicit source classes (pattern/CAD, scan, photo-derived proxy) and capability flags.

### CLO
- Fit workflow starts from real 2D patterns (native or CAD import), sewing and draping on an avatar.
- Provides stress, strain, fit and pressure maps plus garment measurements.
- Auto Fitting adjusts patterns to avatar size; custom avatars require a fitting suit for re-drape.
- Lesson: our current skinned artistic garment is not a substitute for pattern + material + drape simulation. A future “fit map” must be derived from a validated physical/simulation model, not inferred from render proximity.

### Browzwear / VStitcher + Stylezone
- Parametric, imported and “soft” avatars; garment simulation, pose changes, 360 navigation.
- Pressure/tension maps and dedicated fit-review mode.
- 3D styling tools permit local pull/pinch/flatten/alignment corrections.
- Stylezone consumes GLB for review and can preload 3D views.
- Lesson: separate engineering fit review from shopper presentation. Add explicit debug/review overlays and local garment-attachment diagnostics rather than baking manual corrections invisibly into presentation geometry.

### 3DLOOK
- Guided two-photo smartphone capture with pose validation, structured body outputs and API/SDK integration.
- Current Mobile Tailor marketing specifies 80+ measurements and a 3D model from two photos.
- Lesson: customer capture should be a dedicated validated acquisition pipeline with capture-quality checks and privacy lifecycle, not arbitrary photo upload directly into rendering.

### Bold Metrics
- Survey/ML approach rather than photo scanning; combines inferred body measurements/digital twins with brand-specific garment data and shopper fit preference.
- Lesson: measurement acquisition and visual avatar generation need not be the same subsystem. We can support a lower-friction measurement/profile path independently of photorealistic reconstruction.

### Shopify photo-based AI try-on apps
- Shopify currently lists hundreds of “virtual try-on” apps; many are photo/image-generation experiences rather than measurement-grounded 3D fitting.
- Example products emphasize one-photo upload, automatic catalog sync, product-page widget injection and analytics.
- Lesson: photo try-on is a useful **visualization** mode but must remain explicitly separate from our fit-validation path. The strongest integration pattern to borrow is automatic catalog/variant sync + product-page component + reusable customer profile.

## Architecture implications for Knit Riot

1. **Split the product into explicit fidelity layers**
   - Visualization: photorealistic appearance / styling.
   - Geometric sizing: measured avatar + garment grade/ease.
   - Physics: pattern/material/drape simulation.
   - Validation: comparison against actual garment measurements/physical tests.
   Never let a lower layer claim a higher layer’s certainty.

2. **Create a provenance-bearing garment asset contract**
   - source type: pattern/CAD | scan | photo-derived | artistic proxy
   - source garment/SKU/variant/size
   - grade rules and measured dimensions
   - fabric/material test provenance
   - simulation parameters and solver/version
   - validation status and evidence
   - supported capabilities (visual-only, sizing, drape, pressure/strain, etc.)

3. **Persistent shopper digital twin**
   - reusable profile ID independent of a garment
   - body measurements + uncertainty/provenance
   - avatar appearance preferences separate from measurements
   - fit preference separate from anatomy
   - privacy/consent/retention metadata
   - reusable across catalog/Shopify variants.

4. **Garment ingestion should be upstream of the viewer**
   The viewer should consume a prepared garment package rather than inventing garment geometry from body geometry. Pattern/CAD or validated garment measurements should drive grade/ease.

5. **Add engineering review modes**
   - body/garment clearance
   - seam/boundary attachment
   - clipping/intersection
   - garment strain/stress/pressure only when physically meaningful
   - source/validation badge
   - side-by-side sizes and poses.

6. **Shopper UI should stay simple**
   Competitors hide engineering complexity. Keep avatar/profile creation, garment/size choice, fit preference, 360 view, styling, add-to-cart; keep simulation/provenance diagnostics in QA/admin modes.

7. **Catalog integration**
   Plan for Shopify product/variant identifiers, automatic variant/asset mapping, reusable profile, product-page embed/app block, add-to-cart handoff and analytics. Do not write to production Shopify until specifically authorized.

## Current comparison

Knit Riot already has advantages in auditable deterministic QA, GLB round-trip verification, explicit non-validation labeling, real skinned 3D interaction, pose/view coverage and a guarded release gate.

Its largest gaps versus mature fit systems remain: measurement-grounded avatar reconstruction; garment patterns/grade rules; real material properties and drape; validated fit/ease/pressure interpretation; scalable garment digitization; customer-profile lifecycle; and production catalog integration.

Near-term implementation should continue visual cleanup while architecting the provenance-bearing garment package and measurement-driven body/grade layer. Do not delay visual repairs, but do not invest in cosmetic rendering in a way that hard-codes assumptions that conflict with later pattern/physics inputs.
