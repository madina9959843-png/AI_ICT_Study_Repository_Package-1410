# AI-Integrated ICT Course Study — Reproducibility Package

Study title: **From Digital Literacy to AI-Augmented Digital Competence: A Quasi-Experimental Evaluation of an AI-Integrated ICT Course in Higher Education**

## What this repository contains

- `analysis.py` — participant-level analysis workflow used to calculate questionnaire/rubric scores, reliability, paired changes, Hedges-corrected Morris pretest-posttest-control effect sizes (`dppc2`), stratified paired-bootstrap confidence intervals, ANCOVA, longitudinal mixed-effects models, Holm correction, and intercorrelations.
- `verify_effect_sizes_from_summary.py` — independently recomputes the four principal reported `dppc2` point estimates from aggregate means and pre-test SDs reported in the manuscript.
- `reported_results_reference.csv` — aggregate values used by the verification script.
- `codebook.csv` — public data dictionary for questionnaire items, rubric scores, feedback variables, and derived outcomes.
- `DATA_SCHEMA_ONLY_NO_PARTICIPANT_DATA.csv` — header-only schema showing the expected participant-level input format. It contains **no participant records**.
- `Supplementary_Material.docx` — questionnaire, analytic rubric, performance-assessment tasks, intercorrelation tables, and week-by-week intervention schedule.
- `requirements.txt` — software versions reported in the manuscript.

## Important data-availability limitation

A verifiable participant-level analytical dataset is **not included** in this repository.

The workbook previously available during manuscript preparation explicitly labeled its questionnaire responses, rubric scores, follow-up values, feedback values, and group allocation as **synthetic demonstration data**. Those values are not included here and must not be represented as empirical participant records.

The original participant-level research records are not available in a form that can now be independently verified and released as a public de-identified analytical dataset. The authors therefore did **not** reconstruct or generate participant-level records from aggregate statistics.

Accordingly:

- the code is public and documents the analytical workflow;
- the supplementary measurement and intervention materials are public;
- the four principal standardized-effect point estimates can be checked from the aggregate values in `reported_results_reference.csv`;
- full computational reproduction of ANCOVA, mixed-effects models, bootstrap confidence intervals, reliability coefficients, and participant-level correlation analyses requires the original participant-level data and is therefore not possible from this repository alone.

## Expected participant-level input

If a verifiable de-identified participant-level dataset becomes available, save it as a CSV matching `DATA_SCHEMA_ONLY_NO_PARTICIPANT_DATA.csv`.

Required core columns:

- `Participant_ID_Public`
- `Group` (`Control` or `Experimental`)
- `Timepoint` (`T0`, `T1`, `T2`)
- `Q1`–`Q30` (1–5)
- `R1`–`R6` (0–4)

Optional:

- `F1`–`F6` (1–5; post-intervention feedback where actually administered)
- `Program` if institutional/data-protection requirements permit its analytical use

The script derives:

- `D1`–`D6`
- `Overall_Q`
- `Rubric_Total`

## Running the analysis

Python environment reported in the manuscript:

- Python 3.13.5
- NumPy 2.3.5
- pandas 2.2.3
- SciPy 1.17.0
- statsmodels 0.14.6

Install:

```bash
python -m pip install -r requirements.txt
```

Run participant-level analysis when a valid dataset is available:

```bash
python analysis.py --data deidentified_participant_data.csv --outdir results --seed 20261014
```

Verify the four principal reported standardized-effect point estimates from aggregate manuscript values:

```bash
python verify_effect_sizes_from_summary.py
```

## Effect-size definition

The Hedges-corrected Morris pretest-posttest-control standardized effect is

`dppc2 = J * [((Moutcome,E - Mpre,E) - (Moutcome,C - Mpre,C)) / SDpre,pooled]`

where

`SDpre,pooled = sqrt(((nE-1)*SDpre,E^2 + (nC-1)*SDpre,C^2)/(nE+nC-2))`

and

`J = 1 - 3/(4*(nE+nC-2)-1)`.

For T1, `Moutcome` is the immediate post-test mean. For T2, it is the delayed follow-up mean.

The participant-level script estimates 95% CIs using 10,000 stratified paired bootstrap resamples by default. Participants are resampled within study condition while preserving T0-to-outcome pairing.

## Reproducibility statement

This repository maximizes transparency without presenting synthetic or reconstructed individual-level observations as empirical data. It should therefore be interpreted as a **code-and-methods repository**, not as a complete raw-data replication archive.
