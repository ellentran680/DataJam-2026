#!/usr/bin/env python3
"""
DDD $10M BC short term rental case (SFU DSSS DataJam 2026): Parts 1 and 2
Where to buy (location), what to buy (property type) and how many.

Run:  python ddd_analysis.py --data-dir /path/to/inside_airbnb_files --out-dir results

Inputs (Inside Airbnb, Vancouver, CC BY 4.0): listings.csv.gz, calendar.csv.gz, reviews.csv.gz
Outputs: CSV tables in --out-dir that feed the workbook and the slides.

Revenue per listing is Inside Airbnb's estimated_revenue_l365d (an estimate, not reported bookings).
Every cost assumption below has a source note. Full source list with links: SOURCES.md
"""
import argparse, os, re
import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------------------
# 1. ASSUMPTIONS (edit here). Each line says where it comes from.
# ----------------------------------------------------------------------------------------
# Benchmark prices, Aug 2026 (REBGV area benchmarks as reported by Nest Presales; Metro figures match GVR stats)
PRICE = {('West', 'House'): 2932700, ('East', 'House'): 1621400,
         ('West', 'Condo'): 774900,  ('East', 'Condo'): 628600,
         ('West', 'Townhouse'): 1334900, ('East', 'Townhouse'): 985400}
SETUP = {'House': 20000, 'Townhouse': 15000, 'Condo': 10000}    # furnishing: Airbtics 1BR C$4,829; corporatestays $7.5k to 12.5k; Awning $10k to 30k
STRATA = {'House': 0, 'Townhouse': 3780, 'Condo': 3780}          # $0.525/sq ft/month (middle of Vancouver $0.35 to $0.70) x 600 sq ft x 12
INSURANCE = {'House': 3000, 'Townhouse': 2500, 'Condo': 2000}    # STR policies $2,200 to $3,200 in US examples (weakest evidence)
LICENCE = 1108                                                  # City of Vancouver STR business licence per year (vancouver.ca)
CLOSE = 4000                                                    # legal, title insurance, inspection, adjustments (worked example $3,850)
VAR = 0.38        # platform 3% (Airbnb host only fee) + management 20% (middle of 15 to 25%) + utilities, supplies, maintenance 15%
PTAX = 0.00336394 # City of Vancouver 2026 Class 1 residential total rate, $3.36394 per $1,000 (assumes assessed value = benchmark price)

WEST_SIDE = {'Downtown', 'West End', 'Kitsilano', 'Fairview', 'South Cambie', 'Shaughnessy', 'Arbutus Ridge',
             'Kerrisdale', 'Dunbar Southlands', 'West Point Grey', 'Oakridge', 'Marpole'}   # REBGV "Vancouver West"; the rest = East

RECOMMENDED = [('Downtown Eastside', 'Condo', 6), ('Downtown', 'Condo', 5), ('West End', 'Condo', 2)]
BUDGET = 10_000_000


def ptt(p):
    """BC property transfer tax on residential property (gov.bc.ca)."""
    return (0.01 * min(p, 200000) + 0.02 * max(0, min(p, 2000000) - 200000)
            + 0.03 * max(0, min(p, 3000000) - 2000000) + 0.05 * max(0, p - 3000000))


def econ(rev, seg, side, tax_stress=0.0):
    """Return (all in cost, net operating income) for one property given its yearly revenue."""
    p = PRICE[(side, seg)]
    cost = p + ptt(p) + SETUP[seg] + CLOSE
    noi = rev * (1 - VAR) - p * PTAX - STRATA[seg] - INSURANCE[seg] - LICENCE - p * tax_stress
    return cost, noi


# ----------------------------------------------------------------------------------------
# 2. LOAD AND CLEAN
# ----------------------------------------------------------------------------------------
def read_any(path, **kw):
    """Read a CSV whether it is gzip compressed or plain text, whatever the file is called."""
    with open(path, 'rb') as f:
        gz = f.read(2) == b'\x1f\x8b'
    return pd.read_csv(path, compression='gzip' if gz else None, **kw)


def find(data_dir, *names):
    for n in names:
        p = os.path.join(data_dir, n)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f'None of {names} found in {data_dir}')


def licence_class(x):
    if pd.isna(x): return 'none'
    s = str(x)
    if 'xempt' in s: return 'exempt'
    city, prov = bool(re.search(r'\d{2}-\d{6}', s)), bool(re.search(r'H\d{9}', s))
    if city and prov: return 'city+prov'
    if city: return 'city_only'
    if prov: return 'prov_only'
    return 'other'


def bucket(p):
    if p in ('Entire home', 'Entire townhouse', 'Entire cottage', 'Entire villa', 'Entire bungalow'): return 'House/townhouse'
    if p in ('Entire condo', 'Entire rental unit', 'Entire serviced apartment', 'Entire loft'): return 'Condo/apartment'
    if p in ('Entire guest suite', 'Entire guesthouse'): return 'Suite/guesthouse'
    return 'Other'


def segment(r):
    if r.property_type == 'Entire home': return 'House'
    if r.property_type == 'Entire townhouse': return 'Townhouse'
    if r.bucket == 'Condo/apartment': return 'Condo'
    if r.bucket == 'Suite/guesthouse': return 'Suite'
    return 'Other'


def load_listings(path):
    l = read_any(path)
    if 'estimated_revenue_l365d' not in l.columns:
        raise SystemExit('This listings file has too few columns. Use the DETAILED listings file (listings.csv.gz, about 75 columns), not the 18 column summary listings.csv.')
    l['price_num'] = l.price.str.replace(r'[\$,]', '', regex=True).astype(float)   # prices are text in the file
    l['lic'] = l.license.map(licence_class)
    l['bucket'] = l.property_type.map(bucket)
    l['occ'] = l.estimated_occupancy_l365d
    l['rev'] = l.estimated_revenue_l365d
    return l


def analysis_set(l, steps):
    """Decision 1: which listings are comparable for a new, compliant short stay operator."""
    e = l[(l.room_type == 'Entire home/apt') & (l.minimum_nights <= 29) & l.price_num.notna()].copy()
    steps.append(('Entire homes, short stays, with a price', len(e), e.rev.median()))
    a = e[e.lic == 'city+prov']
    steps.append(('+ both city and provincial licence numbers', len(a), a.rev.median()))
    b = a[(a.number_of_reviews_ltm >= 1) | (a.occ > 0)]
    steps.append(('+ some booking activity', len(b), b.rev.median()))
    lo, hi = b.price_num.quantile([.01, .99])
    c = b[(b.price_num >= lo) & (b.price_num <= hi)].copy()
    steps.append((f'+ nightly price within P1 to P99 (${lo:,.0f} to ${hi:,.0f})', len(c), c.rev.median()))
    c['seg'] = c.apply(segment, axis=1)
    c['side'] = np.where(c.neighbourhood_cleansed.isin(WEST_SIDE), 'West', 'East')
    return c


# ----------------------------------------------------------------------------------------
# 3. VALIDATION (sanity checks on the revenue estimate and seasonality)
# ----------------------------------------------------------------------------------------
def validate(a, cal_path, rev_path, out):
    c = read_any(cal_path, parse_dates=['date'])
    c['unavail'] = (c.available == 'f').astype(int)
    cal = c.groupby('listing_id').unavail.mean().rename('cal_unavail')
    v = a.merge(cal, left_on='id', right_index=True, how='left')
    v['ia_occ_share'] = v.occ / 365
    res = {'calendar_unavailable_share_mean': v.cal_unavail.mean(),
           'ia_estimated_occupancy_share_mean': v.ia_occ_share.mean(),
           'correlation_calendar_vs_ia': v[['cal_unavail', 'ia_occ_share']].corr().iloc[0, 1],
           'share_calendar_unavailable_ge_ia_occ': (v.cal_unavail >= v.ia_occ_share).mean(),
           'share_at_255_night_cap': (a.occ >= 255).mean()}
    r = read_any(rev_path, usecols=['listing_id', 'date'], parse_dates=['date'])
    r = r[(r.date >= '2023-01-01') & (r.date < '2026-09-01') & r.listing_id.isin(a.id)]
    s = r.groupby(r.date.dt.month).size()
    seas = (s / s.mean()).rename('review_index').reset_index().rename(columns={'date': 'month'})
    seas.to_csv(os.path.join(out, 'seasonality.csv'), index=False)
    pd.Series(res).rename('value').to_csv(os.path.join(out, 'validation_checks.csv'))
    return res, seas


# ----------------------------------------------------------------------------------------
# 4. YIELD BY AREA AND TYPE (Part 1 and Part 2 evidence)
# ----------------------------------------------------------------------------------------
def yield_by_segment(a, seed=42):
    rng = np.random.default_rng(seed)
    rows = []
    for (nb, seg), g in a[a.seg.isin(['House', 'Condo', 'Townhouse'])].groupby(['neighbourhood_cleansed', 'seg']):
        side = g.side.iloc[0]
        if len(g) < 20: continue
        cost, noi = econ(g.rev.median(), seg, side)
        _, noi25 = econ(g.rev.quantile(.25), seg, side)
        _, noi75 = econ(g.rev.quantile(.75), seg, side)
        bs = [econ(np.median(rng.choice(g.rev.values, len(g))), seg, side)[1] / cost for _ in range(500)]
        rows.append(dict(nb=nb, seg=seg, side=side, n=len(g), rev_med=g.rev.median(), cost=cost, yield_med=noi / cost,
                         yield_p25=noi25 / cost, yield_p75=noi75 / cost,
                         ci_lo=np.percentile(bs, 5), ci_hi=np.percentile(bs, 95)))
    return pd.DataFrame(rows).sort_values('yield_med', ascending=False)


def location_evidence(l, a, seed=3):
    """Part 1: neighbourhood table with occupancy, price, revenue, yield, 90% range and licence share."""
    rng = np.random.default_rng(seed)
    e = l[(l.room_type == 'Entire home/apt') & (l.minimum_nights <= 29)]
    comp = e.groupby('neighbourhood_cleansed').agg(str_listings=('id', 'size'), full_lic_share=('lic', lambda x: (x == 'city+prov').mean()))
    rows = []
    for nb, g in a[a.seg.isin(['Condo', 'House'])].groupby('neighbourhood_cleansed'):
        side = g.side.iloc[0]
        for seg in ['Condo', 'House']:
            s = g[g.seg == seg]
            if len(s) < 10: continue
            cost, noi = econ(s.rev.median(), seg, side)
            bs = [econ(np.median(rng.choice(s.rev.values, len(s))), seg, side)[1] / cost for _ in range(400)]
            rows.append(dict(neighbourhood=nb, type=seg, side=side, n=len(s), median_price_night=s.price_num.median(),
                             median_occ_nights=s.occ.median(), median_rev=s.rev.median(), all_in_cost=cost,
                             net_yield=noi / cost, ci90_lo=np.percentile(bs, 5), ci90_hi=np.percentile(bs, 95)))
    L = pd.DataFrame(rows).merge(comp, left_on='neighbourhood', right_index=True, how='left')
    return L.sort_values('net_yield', ascending=False)


def price_sensitivity(a, areas=('Downtown Eastside', 'Downtown', 'West End')):
    rows = []
    for nb in areas:
        s = a[(a.neighbourhood_cleansed == nb) & (a.seg == 'Condo')]
        side = s.side.iloc[0]
        row = {'area': nb}
        for m in (1.0, 1.1, 1.2, 1.3):
            p = PRICE[(side, 'Condo')] * m
            cost = p + ptt(p) + SETUP['Condo'] + CLOSE
            noi = s.rev.median() * (1 - VAR) - p * PTAX - STRATA['Condo'] - INSURANCE['Condo'] - LICENCE
            row[f'price_x{m:.1f}'] = noi / cost
        rows.append(row)
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------------------
# 5. PORTFOLIOS: few high value vs many condos, stress cases (Part 2)
# ----------------------------------------------------------------------------------------
def simulate(a, seed=7):
    rng = np.random.default_rng(seed)

    def pool(nb, seg):
        v = a[(a.neighbourhood_cleansed == nb) & (a.seg == seg)].rev.values
        return np.minimum(v, np.percentile(v, 95))   # cap at P95 so a few outlier listings do not inflate the mean

    def run(port, label, nsim=20000, rev_mult=1.0, var_add=0.0, tax=0.0):
        cost, draws = 0, []
        for nb, seg, k in port:
            side = a[a.neighbourhood_cleansed == nb].side.iloc[0]
            c0, _ = econ(0, seg, side); cost += c0 * k
            draws.append((nb, seg, side, k))
        tot, rev_tot = np.zeros(nsim), np.zeros(nsim)
        for nb, seg, side, k in draws:
            r = rng.choice(pool(nb, seg), (nsim, k)) * rev_mult
            fixed = -econ(0, seg, side)[1]
            tot += (r * (1 - VAR - var_add) - fixed - PRICE[(side, seg)] * tax).sum(1)
            rev_tot += r.sum(1)
        y = tot / cost
        return dict(portfolio=label, props=sum(k for *_, k in port), deployed=cost,
                    rev_p10=np.percentile(rev_tot, 10), rev_p50=np.percentile(rev_tot, 50), rev_p90=np.percentile(rev_tot, 90),
                    noi_p10=np.percentile(tot, 10), noi_p50=np.percentile(tot, 50), noi_p90=np.percentile(tot, 90),
                    yld_p10=np.percentile(y, 10), yld_p50=np.percentile(y, 50), yld_p90=np.percentile(y, 90))

    compare = pd.DataFrame([run(RECOMMENDED, 'Recommended: 13 condos'),
                            run([('Kitsilano', 'House', 3)], 'Few high value: 3 West side houses'),
                            run([('Kensington-Cedar Cottage', 'House', 5)], 'Mid: 5 East side houses')])
    sc = pd.DataFrame([run(RECOMMENDED, 'Base'), run(RECOMMENDED, 'Revenue -15%', rev_mult=.85),
                       run(RECOMMENDED, 'Revenue -30%', rev_mult=.70), run(RECOMMENDED, 'Opex +10pts', var_add=.10),
                       run(RECOMMENDED, '3% vacancy-type tax', tax=.03), run(RECOMMENDED, 'Upside revenue +10%', rev_mult=1.10)]
                      )[['portfolio', 'deployed', 'noi_p50', 'yld_p10', 'yld_p50', 'yld_p90']]
    conc = pd.DataFrame([run([('Downtown', 'Condo', 12)], '12 Downtown condos only')])
    return compare, sc, conc


def type_and_count(a, seed=11):
    """Part 2: property type comparison and how the yield range narrows as the number of condos grows."""
    t = a[a.seg.isin(['Condo', 'Townhouse', 'House'])].copy()
    t['cost'] = [econ(0, s, sd)[0] for s, sd in zip(t.seg, t.side)]
    t['noi'] = [econ(r, s, sd)[1] for r, s, sd in zip(t.rev, t.seg, t.side)]
    t['yld'] = t.noi / t.cost
    g = t.groupby('seg').agg(n=('id', 'size'), rev_med=('rev', 'median'), cost_med=('cost', 'median'), yld_med=('yld', 'median'),
                             yld_p25=('yld', lambda x: x.quantile(.25)), yld_p75=('yld', lambda x: x.quantile(.75)),
                             share_pos=('yld', lambda x: (x > 0.03).mean()))
    g['rev_per_$1k_cost'] = g.rev_med / g.cost_med * 1000
    g['props_for_10M'] = (BUDGET / g.cost_med).round(1)

    rng = np.random.default_rng(seed)
    pools = {('Downtown Eastside', 'East'): a[(a.neighbourhood_cleansed == 'Downtown Eastside') & (a.seg == 'Condo')].rev.values,
             ('Downtown', 'West'): a[(a.neighbourhood_cleansed == 'Downtown') & (a.seg == 'Condo')].rev.values,
             ('West End', 'West'): a[(a.neighbourhood_cleansed == 'West End') & (a.seg == 'Condo')].rev.values}
    keys, w, rows = list(pools), [.45, .40, .15], []
    for N in [3, 5, 8, 13, 20]:
        ys = []
        for _ in range(5000):
            tot = cost = 0
            for k in rng.choice(len(keys), N, p=w):
                nb, side = keys[k]; v = pools[keys[k]]; v = np.minimum(v, np.percentile(v, 95))
                c, n = econ(rng.choice(v), 'Condo', side); tot += n; cost += c
            ys.append(tot / cost)
        ys = np.array(ys)
        rows.append(dict(N=N, p10=np.percentile(ys, 10), p50=np.percentile(ys, 50), p90=np.percentile(ys, 90),
                         spread=np.percentile(ys, 90) - np.percentile(ys, 10), prob_below_2pct=(ys < .02).mean()))
    return g, pd.DataFrame(rows)


# ----------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-dir', default='/mnt/user-data/uploads')
    ap.add_argument('--out-dir', default='results')
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    pd.options.display.float_format = '{:,.3f}'.format
    pd.options.display.width = 220
    out = lambda n: os.path.join(args.out_dir, n)

    listings = find(args.data_dir, 'listings.csv.gz', 'listings_csv.gz', 'listings.csv')
    calendar = find(args.data_dir, 'calendar.csv.gz', 'calendar_csv_1.gz', 'calendar_csv.gz', 'calendar.csv')
    reviews = find(args.data_dir, 'reviews.csv.gz', 'reviews_csv_1.gz', 'reviews_csv.gz', 'reviews.csv')

    l = load_listings(listings)
    print(f'Listings loaded: {len(l)}; entire homes {int((l.room_type=="Entire home/apt").sum())}')
    steps = []
    a = analysis_set(l, steps)
    S = pd.DataFrame(steps, columns=['step', 'listings', 'median_revenue'])
    S.to_csv(out('decision1_filter_steps.csv'), index=False); print('\nDecision 1: filter steps\n', S.to_string(index=False))
    print('\nAnalysis set by type:', a.seg.value_counts().to_dict())

    res, seas = validate(a, calendar, reviews, args.out_dir)
    print('\nValidation checks:'); [print(f'  {k}: {v:.3f}') for k, v in res.items()]

    Y = yield_by_segment(a); Y.to_csv(out('yield_by_segment.csv'), index=False)
    L = location_evidence(l, a); L.to_csv(out('location_evidence.csv'), index=False)
    print('\nPart 1: condo yield by area (n>=20)\n', L[(L.type == 'Condo') & (L.n >= 20)].to_string(index=False))
    P = price_sensitivity(a); P.to_csv(out('price_sensitivity.csv'), index=False); print('\nPrice sensitivity\n', P.to_string(index=False))

    compare, sc, conc = simulate(a)
    compare.to_csv(out('portfolio_compare.csv'), index=False); sc.to_csv(out('scenarios.csv'), index=False)
    conc.to_csv(out('concentration_test.csv'), index=False)
    print('\nPart 2: portfolios\n', compare[['portfolio', 'props', 'deployed', 'rev_p50', 'noi_p50', 'yld_p10', 'yld_p50', 'yld_p90']].to_string(index=False))
    print('\nStress scenarios\n', sc.to_string(index=False))
    print('\n12 Downtown condos only\n', conc[['portfolio', 'yld_p10', 'yld_p50', 'yld_p90']].to_string(index=False))

    types, how_many = type_and_count(a)
    types.to_csv(out('property_type_comparison.csv')); how_many.to_csv(out('how_many_vs_spread.csv'), index=False)
    print('\nPart 2: property types\n', types.to_string()); print('\nPart 2: how many condos\n', how_many.to_string(index=False))

    cost13 = sum(econ(0, s, a[a.neighbourhood_cleansed == nb].side.iloc[0])[0] * k for nb, s, k in RECOMMENDED)
    print(f'\nRecommended 13 condos: all in cost ${cost13:,.0f}; unspent ${BUDGET - cost13:,.0f}')


if __name__ == '__main__':
    main()
