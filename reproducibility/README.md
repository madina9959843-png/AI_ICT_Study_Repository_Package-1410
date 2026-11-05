# Reproduction package — AI-integrated ICT study

## Inputs and data protection

Place `Akerke_Reproduce_Bootstrap_20261105.py` in the same folder as the author-controlled workbook `Akerke_Analytical_Workbook_Audit_03112026 (1).xlsx`. **The workbook is not bundled** because it contains participant-coded individual responses. Do not publish the participant-level workbook unless sharing is permitted by informed consent and applicable institutional policies.

## Reproduce

Run `python Akerke_Reproduce_Bootstrap_20261105.py` in an environment with `artifact_tool` and NumPy installed. The script reuses one Control and one Experimental 10,000×30 random-index matrix across all outcomes, calls NumPy `default_rng(20261014)` (PCG64), and recomputes baseline pooled SD for every resample. The output is `akerke_bootstrap_results.json`.

## Documentation

`Akerke_Bootstrap_CI_Reconciliation_20261105.csv` contains point estimates, exact 95% interval limits and journal-rounded values. `Akerke_Bootstrap_Statistical_Verification_Protocol_20261105.docx` provides methodology, provenance caveats, and fields for an author-signed paper-to-Excel audit record. This is author-side computational verification, NOT a completed independent external statistical review.

## Important design limitation

One intact class per condition means class effects and intervention effects cannot be disentangled statistically. Participant-level bootstrap intervals describe uncertainty under participant-level resampling and do not correct this cluster confounding.
