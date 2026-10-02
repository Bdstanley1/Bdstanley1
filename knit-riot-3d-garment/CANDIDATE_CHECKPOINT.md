# Knit Riot binding candidate checkpoint

Candidate commit: d01103239ec6f148bcaec1fa2bce2479ed52d595
Base main: 774f232358e3c6d043f864c271a0fadc25d040c6

The latest archived Chromium detail image for tested source 819caed92a605a48a2076748256b8f695bd7e087 still shows light triangular facets along the V-neck and shoulder binding.

This candidate changes the binding to use underlying vest vertex normals, interpolates inward binding joint weights toward the source triangle interior, and caps the in-triangle trim inset at 0.005 m. It also adds 20 upper-garment close-up QA renders: five implemented poses by four defined close-up directions.

Local validated checks:
- immutable-fixture build succeeds; assembled app SHA-256 bfbb4f52124fdeeb043e16cda14b8f774031263bbd8f7cb559ced947f4c31e9b
- Python tool compile succeeds
- refine geometry test passes
- upper-body boundary test passes
- binding geometry test checks 323 boundary edges; maximum inset 0.005 m; maximum triangle-plane error 1.0153553345326749e-16 m; maximum normal-length error 3.3306690738754696e-16; maximum joint-weight-sum error 2.220446049250313e-16
- footwear geometry test passes
- evidence publication unit suite passes 10/10

Pending gate: actual candidate Chromium rerender and image inspection. Visual gate remains NOT_APPROVED and physical fit remains NOT_VALIDATED. Staging is unchanged.
