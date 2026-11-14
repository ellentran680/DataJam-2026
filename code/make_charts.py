"""Slide charts for Part 1 and Part 2. Run after ddd_analysis.py. Usage: python make_charts.py results charts"""
import sys, pandas as pd, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
res, out = (sys.argv[1] if len(sys.argv) > 1 else 'results'), (sys.argv[2] if len(sys.argv) > 2 else 'charts')
L = pd.read_csv(f'{res}/location_evidence.csv'); c = L[(L.type == 'Condo') & (L.n >= 20)].sort_values('net_yield')
fig, ax = plt.subplots(figsize=(8, 4.5))
cols = ['#1f4e9c' if x in ('Downtown Eastside', 'Downtown', 'West End') else '#b0b7c3' for x in c.neighbourhood]
ax.barh(c.neighbourhood, c.net_yield * 100, color=cols, xerr=[(c.net_yield - c.ci90_lo) * 100, (c.ci90_hi - c.net_yield) * 100], ecolor='#444', capsize=3)
ax.set_xlabel('Net yield on all in cost, median condo (%), bars = 90% bootstrap range'); ax.set_title('Condo yield by neighbourhood (areas with 20+ listings)')
plt.tight_layout(); plt.savefig(f'{out}/chart_location_condo_yield.png', dpi=160)
T = pd.read_csv(f'{res}/property_type_comparison.csv')
fig, ax = plt.subplots(figsize=(6.5, 4.2)); ax.bar(T.seg, T.yld_med * 100, color=['#1f4e9c', '#b0b7c3', '#b0b7c3'])
for i, v in enumerate(T.yld_med * 100): ax.text(i, v + 0.05, f'{v:.1f}%', ha='center')
ax.set_ylabel('Median net yield (%)'); ax.set_title('Net yield by property type'); plt.tight_layout(); plt.savefig(f'{out}/chart_type_yield.png', dpi=160)
