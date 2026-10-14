#!/usr/bin/env python3
from pathlib import Path
import csv, math

HERE = Path(__file__).resolve().parent
FILE = HERE / "reported_results_reference.csv"

def pooled_pre_sd(nc, sdc, ne, sde):
    return math.sqrt(((nc - 1) * sdc**2 + (ne - 1) * sde**2) / (nc + ne - 2))

def hedges_j(nc, ne):
    return 1 - 3 / (4 * (nc + ne - 2) - 1)

def dppc2(row):
    nc = int(row["n_control"])
    ne = int(row["n_experimental"])
    mc0 = float(row["pre_mean_control"])
    me0 = float(row["pre_mean_experimental"])
    mc1 = float(row["outcome_mean_control"])
    me1 = float(row["outcome_mean_experimental"])
    sdc = float(row["pre_sd_control"])
    sde = float(row["pre_sd_experimental"])
    sd_pool = pooled_pre_sd(nc, sdc, ne, sde)
    j = hedges_j(nc, ne)
    return j * (((me1 - me0) - (mc1 - mc0)) / sd_pool)

with FILE.open(encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))

print("Verification of principal dppc2 point estimates from reported aggregate statistics")
print("NOTE: bootstrap confidence intervals cannot be independently regenerated from aggregate means/SDs.")
for r in rows:
    calc = dppc2(r)
    rep = float(r["reported_dppc2"])
    print(f'{r["outcome"]} {r["timepoint"]}: calculated={calc:.4f}; reported={rep:.2f}; '
          f'rounds_to_reported={round(calc,2)==round(rep,2)}; '
          f'reported_95CI=[{r["reported_ci_low"]}, {r["reported_ci_high"]}]')
