# Data Availability and Provenance Note — 5 November 2026

**Current public release:** This repository contains no participant-level empirical records. It provides code, schema, codebook, aggregate verification inputs, and methodological supplements only.

**Source records:** The authors report that the participants' Q1–Q30 responses were completed on paper at T0, T1 and T2, manually entered in Excel, and checked by the research team against the original completed questionnaires. The current participant-coded analytical workbook was built using an earlier template that initially held synthetic demonstration data. According to the authors, the demonstration entries were replaced with empirical responses; historical synthetic data must never be described as actual observations.

**Distinctions:** (1) Source-to-transcription checking was performed by the authors; no independent third-party audit of that process has been documented here. (2) Practical rubric score records require separate confirmation against original scoring sheets or artifacts. (3) Independent verification of all reported inference, including ANCOVA, mixed effects, alpha/omega reliability and paired-bootstrap confidence intervals, has not been demonstrated by the files in this public repository.

**Why individual data are not published:** Any release of even pseudonymous participant-level data requires consideration of participant consent, institutional restrictions and re-identification risks. The present public repo is not a participant-level replication archive. Availability of controlled access has not been established.

**Supplementary statistics:** The authors report that Supplementary Tables S5 and S6 were calculated using the current participant-coded workbook, not inferred or reconstructed from aggregate results. This note does not itself constitute independent source or statistical verification.

Older repository statements that the original observations no longer existed are superseded by this clarification. The prior commits are preserved as historical records.

**Revised bootstrap calculations (5 November 2026):** A versioned computational script and an aggregate CI reconciliation are available in `reproducibility/`. The corrected 95% percentile CI for the overall T1 questionnaire effect is [1.08, 1.85]. These files allow recomputation when the authorized private participant-coded workbook is supplied to the analyst; they do not make private records public, nor do they constitute an independent external review.
