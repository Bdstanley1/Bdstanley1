# Owner mobile QA — 2026-10-01

Evidence: owner-tested staging on physical iPhone (screenshots supplied in chat). Treat as physical-device usability evidence, not automated Chromium emulation.

Required corrections:
1. When model controls are minimized/hidden, move/reframe the model toward the top of the available stage instead of leaving it low with large empty space.
2. Add genuinely distinct shoe choices beyond current white slip-ons/barefoot. Do not add fake choices that reuse identical geometry.
3. Hair labels/colors are wrong or misleading in current UI: “Original hair” renders blonde/light; “Blonde” appears strawberry. Calibrate visible swatches/labels to actual rendered color and preserve an explicit original/source option if needed.
4. Add a broader useful range of skin-tone material options. Continue labeling them as material appearance choices, not verified ethnicity.
5. Selecting a camera preset must remain selected while the user interacts with controls. Merely touching the render surface must not switch the visible preset to Free. Switch to Free only after an actual orbit/drag changes camera orientation.
6. Remove +/- zoom buttons from mobile UI. Use pinch for zoom.
7. Allow direct drag manipulation of the model/view on the render surface (orbit/reposition interaction as appropriate) while preserving preset behavior and avoiding accidental mode changes on tap.
8. Owner screenshots show severe framing/interaction failures after some touch/height/length operations: tiny/offscreen model and apparent detached/floating geometry. Reproduce and repair; add physical-mobile-derived regression cases to automated QA where feasible.

Acceptance requires actual rendered/interaction testing, including phone portrait controls and gesture interactions. Do not mark resolved based only on DOM state.
