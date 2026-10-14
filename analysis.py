#!/usr/bin/env python3
"""
Participant-level analysis workflow for:
From Digital Literacy to AI-Augmented Digital Competence:
A Quasi-Experimental Evaluation of an AI-Integrated ICT Course in Higher Education

IMPORTANT:
This repository does not include the original participant-level analytical dataset.
Run this script only on a verifiable de-identified participant-level CSV matching
DATA_SCHEMA_ONLY_NO_PARTICIPANT_DATA.csv.

The script never reconstructs participant-level observations from aggregate results.
"""
from __future__ import annotations

import argparse
import itertools
import math
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.multivariate.factor import Factor

Q = [f"Q{i}" for i in range(1,31)]
R = [f"R{i}" for i in range(1,7)]
F = [f"F{i}" for i in range(1,7)]
DOMAINS = {
    "D1": [f"Q{i}" for i in range(1,6)],
    "D2": [f"Q{i}" for i in range(6,11)],
    "D3": [f"Q{i}" for i in range(11,16)],
    "D4": [f"Q{i}" for i in range(16,21)],
    "D5": [f"Q{i}" for i in range(21,26)],
    "D6": [f"Q{i}" for i in range(26,31)],
}
SCORES = ["Overall_Q", "D1","D2","D3","D4","D5","D6","Rubric_Total"]

def holm_adjust(pvals):
    pvals = np.asarray(pvals, dtype=float)
    m = len(pvals)
    order = np.argsort(pvals)
    out = np.empty(m, dtype=float)
    running = 0.0
    for rank, idx in enumerate(order):
        adj = (m-rank) * pvals[idx]
        running = max(running, adj)
        out[idx] = min(1.0, running)
    return out

def cronbach_alpha(x):
    x = pd.DataFrame(x).dropna()
    k = x.shape[1]
    if k < 2 or len(x) < 2:
        return np.nan
    item_var = x.var(axis=0, ddof=1).sum()
    total_var = x.sum(axis=1).var(ddof=1)
    if total_var <= 0:
        return np.nan
    return (k/(k-1)) * (1-item_var/total_var)

def omega_total_one_factor(x):
    """McDonald's omega total from a standardized one-factor ML congeneric model."""
    x = pd.DataFrame(x).dropna()
    if x.shape[0] < max(10, x.shape[1] + 2):
        return np.nan
    z = (x - x.mean()) / x.std(ddof=1)
    z = z.replace([np.inf,-np.inf], np.nan).dropna()
    if len(z) < 3:
        return np.nan
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = Factor(z.to_numpy(), n_factor=1, method="ml").fit()
    lam = np.asarray(res.loadings)[:,0]
    uniq = np.asarray(res.uniqueness)
    numerator = float(np.sum(lam)**2)
    denom = numerator + float(np.sum(uniq))
    return numerator/denom if denom > 0 else np.nan

def validate_and_score(df):
    required = {"Participant_ID_Public","Group","Timepoint",*Q,*R}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))

    df = df.copy()
    if not set(df["Group"].dropna().unique()).issubset({"Control","Experimental"}):
        raise ValueError("Group must contain only Control/Experimental.")
    if not set(df["Timepoint"].dropna().unique()).issubset({"T0","T1","T2"}):
        raise ValueError("Timepoint must contain only T0/T1/T2.")

    for c in Q:
        bad = df[c].dropna()[~df[c].dropna().between(1,5)]
        if len(bad):
            raise ValueError(f"{c} contains values outside 1-5.")
    for c in R:
        bad = df[c].dropna()[~df[c].dropna().between(0,4)]
        if len(bad):
            raise ValueError(f"{c} contains values outside 0-4.")
    for c in F:
        if c in df:
            bad = df[c].dropna()[~df[c].dropna().between(1,5)]
            if len(bad):
                raise ValueError(f"{c} contains values outside 1-5.")

    dup = df.duplicated(["Participant_ID_Public","Timepoint"])
    if dup.any():
        raise ValueError("Duplicate Participant_ID_Public x Timepoint rows detected.")

    group_counts = df.groupby("Participant_ID_Public")["Group"].nunique(dropna=True)
    if (group_counts > 1).any():
        raise ValueError("At least one participant changes Group across measurement occasions.")

    for d, cols in DOMAINS.items():
        df[d] = df[cols].mean(axis=1) if not df[cols].isna().any(axis=1).all() else np.nan
        df.loc[df[cols].isna().any(axis=1), d] = np.nan
    df["Overall_Q"] = df[Q].mean(axis=1)
    df.loc[df[Q].isna().any(axis=1), "Overall_Q"] = np.nan
    df["Rubric_Total"] = df[R].sum(axis=1)
    df.loc[df[R].isna().any(axis=1), "Rubric_Total"] = np.nan
    return df

def descriptives(df):
    rows=[]
    for outcome in SCORES:
        for (g,t), sub in df.groupby(["Group","Timepoint"]):
            s=sub[outcome].dropna()
            if len(s):
                sem=s.std(ddof=1)/math.sqrt(len(s))
                crit=stats.t.ppf(.975, len(s)-1) if len(s)>1 else np.nan
                rows.append([outcome,g,t,len(s),s.mean(),s.std(ddof=1),
                             s.mean()-crit*sem if len(s)>1 else np.nan,
                             s.mean()+crit*sem if len(s)>1 else np.nan])
    return pd.DataFrame(rows, columns=["Outcome","Group","Timepoint","n","Mean","SD","CI_low","CI_high"])

def reliability(df):
    rows=[]
    for t in ["T0","T1"]:
        sub=df[df.Timepoint.eq(t)]
        blocks={**DOMAINS, "Overall":Q}
        for name,cols in blocks.items():
            rows.append([t,name,len(sub),cronbach_alpha(sub[cols]),omega_total_one_factor(sub[cols])])
    return pd.DataFrame(rows,columns=["Timepoint","Scale","n","Cronbach_alpha","Omega_total"])

def paired_change_tests(df, outcome, time1="T1"):
    wide=df.pivot(index="Participant_ID_Public",columns="Timepoint",values=outcome)
    groups=df.drop_duplicates("Participant_ID_Public").set_index("Participant_ID_Public")["Group"]
    rows=[]
    for g in ["Control","Experimental"]:
        ids=groups[groups.eq(g)].index
        x=wide.reindex(ids)[["T0",time1]].dropna()
        tt=stats.ttest_rel(x[time1],x["T0"])
        change=x[time1]-x["T0"]
        rows.append([outcome,g,f"T0->{time1}",len(x),change.mean(),change.std(ddof=1),tt.statistic,tt.pvalue])
    return rows

def pooled_pre_sd(c0,e0):
    nc,ne=len(c0),len(e0)
    return math.sqrt(((nc-1)*c0.std(ddof=1)**2 + (ne-1)*e0.std(ddof=1)**2)/(nc+ne-2))

def hedges_j(nc,ne):
    return 1 - 3/(4*(nc+ne-2)-1)

def dppc2_from_arrays(c0,c1,e0,e1):
    c=pd.concat([c0,c1],axis=1).dropna()
    e=pd.concat([e0,e1],axis=1).dropna()
    c0a,c1a=c.iloc[:,0],c.iloc[:,1]
    e0a,e1a=e.iloc[:,0],e.iloc[:,1]
    sd=pooled_pre_sd(c0a,e0a)
    return hedges_j(len(c0a),len(e0a))*(((e1a.mean()-e0a.mean())-(c1a.mean()-c0a.mean()))/sd)

def effect_size(df,outcome,outcome_time="T1",n_boot=10000,seed=20261014):
    piv=df.pivot(index="Participant_ID_Public",columns="Timepoint",values=outcome)
    groups=df.drop_duplicates("Participant_ID_Public").set_index("Participant_ID_Public")["Group"]

    cids=groups[groups.eq("Control")].index
    eids=groups[groups.eq("Experimental")].index
    c=piv.reindex(cids)[["T0",outcome_time]].dropna()
    e=piv.reindex(eids)[["T0",outcome_time]].dropna()
    point=dppc2_from_arrays(c["T0"],c[outcome_time],e["T0"],e[outcome_time])

    rng=np.random.default_rng(seed)
    boot=np.empty(n_boot,float)
    for i in range(n_boot):
        ci=rng.integers(0,len(c),len(c))
        ei=rng.integers(0,len(e),len(e))
        cs=c.iloc[ci]
        es=e.iloc[ei]
        boot[i]=dppc2_from_arrays(cs["T0"],cs[outcome_time],es["T0"],es[outcome_time])
    lo,hi=np.quantile(boot,[.025,.975])
    return [outcome,outcome_time,len(c),len(e),point,lo,hi,n_boot,seed]

def ancova(df,outcome):
    w=df.pivot(index="Participant_ID_Public",columns="Timepoint",values=outcome)
    g=df.drop_duplicates("Participant_ID_Public").set_index("Participant_ID_Public")["Group"]
    x=pd.concat([w[["T0","T1"]],g],axis=1).dropna()
    x["Experimental"]=(x["Group"]=="Experimental").astype(int)
    X=sm.add_constant(x[["T0","Experimental"]])
    model=sm.OLS(x["T1"],X).fit()
    b=model.params["Experimental"]
    ci=model.conf_int().loc["Experimental"].tolist()
    t=model.tvalues["Experimental"]
    f=t*t
    p=model.pvalues["Experimental"]
    eta=f/(f+model.df_resid)
    return [outcome,len(x),b,ci[0],ci[1],f,model.df_resid,p,eta]

def mixed_model(df,outcome):
    d=df[["Participant_ID_Public","Group","Timepoint",outcome]].dropna().copy()
    d=d.rename(columns={outcome:"Y"})
    d["Group"]=pd.Categorical(d["Group"],categories=["Control","Experimental"])
    d["Timepoint"]=pd.Categorical(d["Timepoint"],categories=["T0","T1","T2"])
    full=smf.mixedlm("Y ~ C(Group) * C(Timepoint)",d,groups=d["Participant_ID_Public"]).fit(reml=False,method="lbfgs")
    reduced=smf.mixedlm("Y ~ C(Group) + C(Timepoint)",d,groups=d["Participant_ID_Public"]).fit(reml=False,method="lbfgs")
    lr=2*(full.llf-reduced.llf)
    df_diff=max(1,int(round(full.df_modelwc-reduced.df_modelwc)))
    p_lrt=stats.chi2.sf(lr,df_diff)

    names=list(full.params.index)
    t1=[n for n in names if "C(Group)[T.Experimental]:C(Timepoint)[T.T1]" in n]
    t2=[n for n in names if "C(Group)[T.Experimental]:C(Timepoint)[T.T2]" in n]
    def coef(name_list):
        if not name_list:
            return [np.nan,np.nan,np.nan,np.nan]
        n=name_list[0]
        ci=full.conf_int().loc[n]
        return [full.params[n],ci.iloc[0],ci.iloc[1],full.pvalues[n]]
    return [outcome,lr,df_diff,p_lrt,*coef(t1),*coef(t2)]

def correlation_outputs(df):
    result={}
    for time in ["T0","T1"]:
        s=df[df.Timepoint.eq(time)][list(DOMAINS)]
        result[f"corr_{time}.csv"]=s.corr(method="pearson")
    wide={}
    for d in DOMAINS:
        wide[d]=df.pivot(index="Participant_ID_Public",columns="Timepoint",values=d)
    groups=df.drop_duplicates("Participant_ID_Public").set_index("Participant_ID_Public")["Group"]
    for g in ["Control","Experimental"]:
        ids=groups[groups.eq(g)].index
        changes=pd.DataFrame({d:(wide[d].reindex(ids)["T1"]-wide[d].reindex(ids)["T0"]) for d in DOMAINS})
        result[f"corr_change_{g.lower()}.csv"]=changes.corr(method="pearson")
    return result

def fisher_freeman_halton_2xk(table):
    """
    Exact two-sided Fisher-Freeman-Halton test for a 2 x k table with fixed margins.
    Two-sided p sums tables with probability <= observed table probability.
    Intended for small/moderate tables.
    """
    a=np.asarray(table,dtype=int)
    if a.ndim!=2 or a.shape[0]!=2:
        raise ValueError("Expected a 2 x k contingency table.")
    col=a.sum(axis=0)
    n1=a[0].sum()
    N=a.sum()
    denom=math.comb(int(N),int(n1))
    def prob(x):
        num=1
        for cj,xj in zip(col,x):
            num*=math.comb(int(cj),int(xj))
        return num/denom
    obs=prob(a[0])
    p=0.0
    def rec(j,remaining,prefix):
        nonlocal p
        if j==len(col)-1:
            x=remaining
            if 0<=x<=col[j]:
                v=prefix+[x]
                pv=prob(v)
                if pv <= obs + 1e-15:
                    p += pv
            return
        lo=max(0, remaining-int(col[j+1:].sum()))
        hi=min(int(col[j]), remaining)
        for x in range(lo,hi+1):
            rec(j+1,remaining-x,prefix+[x])
    rec(0,int(n1),[])
    return min(1.0,p)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data",required=True,help="De-identified participant-level CSV.")
    ap.add_argument("--outdir",default="results")
    ap.add_argument("--seed",type=int,default=20261014)
    ap.add_argument("--bootstrap",type=int,default=10000)
    args=ap.parse_args()

    out=Path(args.outdir)
    out.mkdir(parents=True,exist_ok=True)
    df=pd.read_csv(args.data)
    df=validate_and_score(df)

    descriptives(df).to_csv(out/"descriptives.csv",index=False)
    reliability(df).to_csv(out/"reliability.csv",index=False)

    paired=[]
    for y in ["Overall_Q","Rubric_Total"]:
        paired.extend(paired_change_tests(df,y,"T1"))
    pd.DataFrame(paired,columns=["Outcome","Group","Comparison","n","Mean_change","SD_change","t","p"]).to_csv(out/"paired_changes.csv",index=False)

    effects=[]
    for y in SCORES:
        effects.append(effect_size(df,y,"T1",args.bootstrap,args.seed))
    for y in ["Overall_Q","Rubric_Total"]:
        effects.append(effect_size(df,y,"T2",args.bootstrap,args.seed+1))
    pd.DataFrame(effects,columns=["Outcome","Outcome_time","n_control","n_experimental","dppc2","CI_low","CI_high","bootstrap_resamples","seed"]).to_csv(out/"effect_sizes.csv",index=False)

    anc=[ancova(df,y) for y in ["D1","D2","D3","D4","D5","D6"]]
    ancdf=pd.DataFrame(anc,columns=["Outcome","n","B_group","CI_low","CI_high","F","df_resid","raw_p","partial_eta2"])
    ancdf["holm_p"]=holm_adjust(ancdf["raw_p"].to_numpy())
    ancdf.to_csv(out/"domain_ancova.csv",index=False)

    mixed=[mixed_model(df,y) for y in SCORES]
    mixdf=pd.DataFrame(mixed,columns=[
        "Outcome","LRT_chi2","LRT_df","LRT_raw_p",
        "Exp_x_T1_B","Exp_x_T1_CI_low","Exp_x_T1_CI_high","Exp_x_T1_p",
        "Exp_x_T2_B","Exp_x_T2_CI_low","Exp_x_T2_CI_high","Exp_x_T2_p"])
    domain_mask=mixdf["Outcome"].isin(["D1","D2","D3","D4","D5","D6"])
    mixdf["LRT_holm_p"]=np.nan
    mixdf.loc[domain_mask,"LRT_holm_p"]=holm_adjust(mixdf.loc[domain_mask,"LRT_raw_p"].to_numpy())
    mixdf.to_csv(out/"mixed_models.csv",index=False)

    for filename,mat in correlation_outputs(df).items():
        mat.to_csv(out/filename)

    if "Program" in df.columns:
        tmp=df.drop_duplicates("Participant_ID_Public")
        tab=pd.crosstab(tmp["Group"],tmp["Program"])
        if tab.shape[0]==2:
            pd.DataFrame([{"p_exact":fisher_freeman_halton_2xk(tab.to_numpy())}]).to_csv(out/"program_distribution_exact_test.csv",index=False)

    if all(c in df.columns for c in F):
        fb=df[(df.Group=="Experimental") & (df.Timepoint=="T1")][F]
        summary=pd.DataFrame({"M":fb.mean(),"SD":fb.std(ddof=1),"n":fb.count()})
        summary.to_csv(out/"experimental_feedback.csv")

    print(f"Analysis complete. Results written to: {out.resolve()}")

if __name__=="__main__":
    main()
