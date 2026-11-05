# AI-Integrated ICT Course Study — Reproducibility Package

Study: *From Digital Literacy to AI-Augmented Digital Competence: A Quasi-Experimental Evaluation of an AI-Integrated ICT Course in Higher Education*

## Purpose and contents

This repository contains the public code-and-methods package for the study. It does **not** contain a publicly released participant-level empirical dataset.

- `analysis.py`: analytical workflow for questionnaire/rubric scoring, reliability, paired comparisons, Morris/Hedges `dppc2`, paired bootstrap confidence intervals, ANCOVA, mixed-effects analyses, Holm adjustments and correlations. Availability of a script does not independently certify its published outputs.
- `verify_effect_sizes_from_summary.py` and `reported_results_reference.csv`: reproducibility checks for selected point estimates based on published aggregate statistics; they do not reproduce participant-level inference.
- `codebook.csv`: data dictionary.
- `DATA_SCHEMA_ONLY_NO_PARTICIPANT_DATA.csv`: empty dataset schema, not empirical observations.
- `Supplementary_Material_S1-S6_20261105.docx`: author-prepared methodological supplements S1–S6, including descriptive statistics and exploratory correlation matrices; do not interpret this file as independent statistical validation.
- `requirements.txt`: repository software requirements, if present in the existing repository. New bootstrap-specific instructions are provided in `reproducibility/README.md`.

## Update files dated 5 November 2026

This package supplies `README.md`, `DATA_AVAILABILITY_NOTE.md`, `Supplementary_Material_S1-S6_20261105.docx`, and the reproducibility subdirectory. The latter contains a bootstrap script requiring access to an **authorized private** Excel workbook, an aggregate bootstrap-CI reconciliation CSV, a methodological protocol, and usage instructions. It contains no participant-level empirical observations.

The bootstrap point estimates and percentile intervals match the version of the manuscript revised on 5 November 2026. In particular, the primary T1 questionnaire effect is dppc2 = 1.36 with 95% CI [1.08, 1.85].

**Do not upload** an author workbook with Q1–Q30/R1–R6 individual records, a participant roster, or paper questionnaire scans without a separate authorization and de-identification review.

## Origin of participant-level observations

The research team reports that the 60 participants completed **paper-based questionnaires** at T0 (pre-test), T1 (post-test) and T2 (four-week follow-up). The authors manually entered the responses in an Excel workbook under pseudonymous participant identifiers S001–S060. The authors also report having checked the questionnaire transcriptions against the original completed paper questionnaires.

**Historical template clarification.** The workbook initially contained **synthetic demonstration data** used to test the data layout and analytical workflow. The authors state that these demonstration entries were subsequently replaced with actual questionnaire responses. The synthetic demonstration data are **not** empirical research observations and must not be cited or released as such. The historical synthetic workbook and the subsequent empirical analytical workbook are different stages in the data-processing history.

This author-performed paper-to-Excel check is **not** an independent third-party audit. Provenance of the practical performance-rubric scoring records (R1–R6) requires separate verification against original scored work or rating sheets.

## Supplementary statistics S5 and S6

The authors' revised supplementary materials include:

- **S5:** six domain-level means and sample standard deviations by group and measurement occasion (T0, T1, T2).
- **S6:** Pearson inter-dimension correlations by study condition at T0 and T1 and Pearson correlations among T1−T0 change scores.

The supplementary tables were calculated from the participant-coded workbook the authors identify as their empirically transcribed dataset. These matrices are descriptive and **do not provide factorial validation**.

## Public data access and reproducibility limitations

No participant-level questionnaire or rubric records are deposited in this public repository. The original paper questionnaires and participant-coded analytical workbook are retained by the research team, as reported by the authors. Any controlled access is subject to institutional data governance, consent terms, de-identification and appropriate safeguards. **Do not upload names, the linkage key, paper scans or participant-level files to this public repository without the required authorization.**

Consequently, code and aggregate data in this repository alone are **insufficient to reproduce** ANCOVA, longitudinal mixed-effects models, participant-level reliability estimates or bootstrap confidence intervals independently. The paper-to-Excel check does not replace an independent statistical review. No completed independent statistician's report is represented here.

One intact class was assigned to each condition. Any estimated between-group difference is therefore confounded with possible unmeasured class-level differences and should be interpreted as an association rather than definitive causal identification.

## Expected input for analyses

The private study dataset, when used by authorized researchers, should follow `DATA_SCHEMA_ONLY_NO_PARTICIPANT_DATA.csv` with participant code, group, timepoint, Q1–Q30 responses on the 1–5 scale and R1–R6 ratings on the 0–4 scale. Optional feedback variables and program codes should only be used when legitimately collected and authorized.

For the software environment, instructions and effect-size definitions, consult `requirements.txt`, `analysis.py` (if present in the existing repository), `reproducibility/README.md`, and the methods in the accompanying manuscript. Do not assume the analysis has been independently replicated simply because a script runs.

## Repository update note (5 November 2026)

This README clarifies the provenance of the research team's analytical workbook and corrects older wording that suggested participant-level observations were lost. The participant-coded dataset remains nonpublic. Historical repository commits showing the old demonstration-only statement are retained for transparency rather than rewritten or concealed.
