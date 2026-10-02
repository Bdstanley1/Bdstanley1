# Future customer capture, private profile and scene options

Owner requirements recorded 2026-10-01. These are product requirements, not claims that measurement accuracy is already validated.

## 1. Guided 360-degree video body capture

Offer an optional phone/laptop-camera capture that guides the customer through an approximately vertical-axis turn while trying to keep body translation and pose changes small.

The UI should:
- recommend close-fitting, non-compressive clothing that exposes body silhouette without materially reshaping it; give concrete examples and warn against loose garments;
- give camera placement, distance, lighting, hair, footwear and posture guidance;
- use an explicit calibration/reference method sufficient to recover scale; do not infer absolute dimensions from uncalibrated monocular pixels;
- provide live visual + spoken guidance for centering, framing, turn speed, arm position, occlusion, camera stability and excessive x/y translation;
- detect unsuitable frames/poses and request a repeat rather than silently estimating;
- reconstruct body geometry/measurements with per-measurement uncertainty/confidence and acquisition provenance;
- validate the pipeline against independently measured bodies before presenting it as measurement accurate.

The customer should not have to rotate perfectly around a mathematical z-axis. The capture/reconstruction pipeline should estimate camera/body pose and compensate for modest translation/rotation errors where validated; excessive motion should trigger recapture.

## 2. Identity / face choices

Offer clearly separate choices:
- use a stock/selectable lifelike model face;
- create/use a non-identifying avatar face;
- optionally use the customer's own face with explicit informed consent.

Face appearance is separate from measured body geometry and fit. A customer can use accurate body measurements without exposing/storing facial identity.

Do not transmit, publish or retain real face/body imagery beyond the explicitly consented purpose and retention period.

## 3. Guided manual measurement mode

Provide visual and spoken instructions for each required measurement, including anatomical landmarks, tape orientation/tension, posture and common mistakes.

Allow measurement entry by:
- keyboard/touch;
- voice, with read-back confirmation before accepting values;
- camera-assisted measurement only where the calibration/method has been validated.

Support unit selection and plausibility/consistency checks. Store the acquisition method and uncertainty/provenance for every value.

## 4. Privacy-preserving reusable profile

Allow a customer to save a reusable profile without requiring public identity.

Architectural requirements:
- random/pseudonymous profile identifier rather than name as the primary key;
- body measurements/geometry separate from face imagery and account/contact information;
- appearance preferences separate from anatomy;
- fit preference separate from body measurements;
- consent and retention metadata;
- encryption in transit and at rest when a backend is introduced;
- least-privilege access and no customer data in public GitHub/CI/logs;
- export/delete controls;
- local/on-device processing/storage where practical, especially raw capture frames;
- derived measurement/body data should be independently deletable with clear retention rules.

Do not claim anonymity merely because a name is removed: body/face imagery and detailed body geometry can still be identifying.

## 5. Background / scene choice

Offer selectable backgrounds independent of avatar/body/garment:
- neutral studio;
- light/dark simple backgrounds;
- retail/fitting-room scenes;
- lifestyle scenes as appropriate;
- optional customer-selected background only with consent/privacy handling.

Background choice must not alter body measurements, garment simulation or fit results. It is presentation only. Keep a neutral calibrated scene available for fit inspection and QA.

## Product-flow proposal

Choose experience:
1. **Browse on a model** — choose a lifelike stock model, appearance and background.
2. **My Body** — guided 360 capture OR guided manual measurements.
3. Optional face choice — stock model face / avatar / customer's face.
4. Save private reusable profile if desired.
5. Dress profile/model, compare sizes and inspect fit evidence.
6. Clearly show which outputs are visualization, measured, inferred, simulated or physically validated.

## Validation gates

Before release of automatic measurement:
- define calibration method and capture protocol;
- build a consent/privacy threat model;
- establish reference measurement protocol and test population;
- quantify bias/error by measurement and relevant body-size ranges;
- test clothing, hair, lighting, pose, camera distance/lens and motion sensitivity;
- define recapture thresholds;
- report uncertainty rather than hiding low-confidence estimates.

No camera-derived measurement, fit recommendation, pressure/comfort prediction or identity-protection claim should be presented as validated until corresponding evidence exists.
