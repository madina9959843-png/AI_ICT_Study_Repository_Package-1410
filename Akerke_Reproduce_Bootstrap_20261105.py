"""Reproduce bootstrap dppc2 and 95% percentile CI from participant-level data.
Requires: pip install artifact-tool numpy. Place this script beside the author workbook.
No participant names or IDs are written to result files."""

from artifact_tool import Blob, SpreadsheetFile
import numpy as np, json, os
from pathlib import Path
root=Path(__file__).resolve().parent
w=SpreadsheetFile.import_xlsx(Blob.load(str(root/'Akerke_Analytical_Workbook_Audit_03112026 (1).xlsx')))
data={}
for t in ['T0','T1','T2']:
 s=w.worksheets.get_item('RAW_'+t)
 rows=s.get_range('A1:AR61' if t=='T1' else 'A1:AL61').values
 header=rows[0]
 # headers checked against expected 30 questionnaire items and six rubric items
 data[t]={}
 for r in rows[1:]:
  if not r[0]:continue
  q=np.array([float(r[header.index('Q'+str(i))]) for i in range(1,31)])
  rub=np.array([float(r[header.index('R'+str(i))]) for i in range(1,7)])
  data[t][r[0]]={'group':r[1],'Q':q,'Rubric':rub}
ids={grp: sorted([i for i,v in data['T0'].items() if v['group']==grp]) for grp in ['Control','Experimental']}
assert [len(ids['Control']),len(ids['Experimental'])]==[30,30]
J=1-3/(4*(60-2)-1)
arr={}
for grp in ids:
 arr[grp]={}
 for outcome in ['Overall','Rubric']+[f'D{x}' for x in range(1,7)]:
  arr[grp][outcome]={}
  for t in ['T0','T1','T2']:
   v=[]
   for sid in ids[grp]:
    x=data[t][sid]
    if outcome=='Overall': z=x['Q'].mean()
    elif outcome=='Rubric': z=x['Rubric'].sum()
    else:
     k=int(outcome[1:])-1
     z=x['Q'][k*5:(k+1)*5].mean()
    v.append(z)
   arr[grp][outcome][t]=np.array(v)
seed=20261014
# exact reproducibility pre-generate matched pairs by group; reuse across outcomes
rng=np.random.default_rng(seed)
B=10000
ix={grp:rng.integers(0,30,(B,30)) for grp in ids}
res={}
for outcome in arr['Control']:
 res[outcome]={}
 c0=arr['Control'][outcome]['T0'];e0=arr['Experimental'][outcome]['T0']
 std=np.sqrt((29*np.var(c0,ddof=1)+29*np.var(e0,ddof=1))/58)
 for t in ['T1','T2']:
  c=arr['Control'][outcome][t];e=arr['Experimental'][outcome][t]
  d=(e-e0).mean()-(c-c0).mean()
  point=J*d/std
  cs=ix['Control'];es=ix['Experimental']
  change=(e[es]-e0[es]).mean(axis=1)-(c[cs]-c0[cs]).mean(axis=1)
  sd=np.sqrt((29*np.var(c0[cs],axis=1,ddof=1)+29*np.var(e0[es],axis=1,ddof=1))/58)
  db=J*change/sd
  dbfixed=J*change/std
  lo,hi=np.quantile(db,[.025,.975]);lofix,hifix=np.quantile(dbfixed,[.025,.975]);
  res[outcome][t]={'point':point,'percentile_refit':[lo,hi],'percentile_fixed_sd':[lofix,hifix], 'difference':d}
  print(f'{outcome:10} {t} point={point:.6f} recompute_SD_CI=[{lo:.4f}, {hi:.4f}] fixedSD_CI=[{lofix:.4f},{hifix:.4f}]')
with open(root/'akerke_bootstrap_results.json','w') as f:json.dump({'seed':seed,'B':B,'J':J,'res':res},f,indent=2)
