#!/usr/bin/env python3
"""
DDD case, Part 3 (expected 2027 performance and financial analysis) and Part 4 (risk).
Run AFTER ddd_analysis.py (it reuses the same cleaning, assumptions and results folder).

  python code/ddd_part3_part4.py --data-dir "." --out-dir results
"""
import argparse, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ddd_analysis as d

POLICY_RATE = 0.025       # Bank of Canada overnight rate, 2.50% since Oct 28 2026 (bankofcanada.ca)
APT_PRICE_YOY = -0.066    # GVR Aug 2026: Metro Vancouver apartment benchmark down 6.6% from Aug 2025 (gvrealtors.ca)
APT_PRICE_YOY_OCT = -0.059  # GVR Oct 2026 apartment benchmark down 5.9% year over year (as reported by mortgagesandbox.com)
AREAS = {'Downtown Eastside': ('East', 6), 'Downtown': ('West', 5), 'West End': ('West', 2)}   # units per area, from Part 2


def base_revenue(a):
    """Base case revenue per condo: mean of listing revenue after capping at the 95th percentile (same as Part 2 simulation)."""
    out = {}
    for nb in AREAS:
        v = a[(a.neighbourhood_cleansed == nb) & (a.seg == 'Condo')].rev.values
        out[nb] = dict(base=np.minimum(v, np.percentile(v, 95)).mean(), median=np.median(v),
                       p25=np.percentile(v, 25), p75=np.percentile(v, 75), n=len(v))
    return out


def portfolio(rev, rev_mult=1.0, platform=0.03, mgmt=0.20, other=0.15, price_mult=1.0, strata_sqft=0.525,
              insurance=None, setup=None, levy=0.0, scenario='base'):
    """Full portfolio P&L for the 13 condos with any driver overridden. Returns dict of totals."""
    tot = dict(units=0, cost=0, revenue=0, platform=0, mgmt=0, other=0, prop_tax=0, strata=0, insurance=0, licence=0, levy=0)
    for nb, (side, k) in AREAS.items():
        p = d.PRICE[(side, 'Condo')] * price_mult
        cost = p + d.ptt(p) + (setup if setup is not None else d.SETUP['Condo']) + d.CLOSE
        r = rev[nb][scenario] * rev_mult
        tot['units'] += k; tot['cost'] += cost * k; tot['revenue'] += r * k
        tot['platform'] += r * platform * k; tot['mgmt'] += r * mgmt * k; tot['other'] += r * other * k
        tot['prop_tax'] += p * d.PTAX * k; tot['strata'] += strata_sqft * 600 * 12 * k
        tot['insurance'] += (insurance if insurance is not None else d.INSURANCE['Condo']) * k
        tot['licence'] += d.LICENCE * k; tot['levy'] += p * levy * k
    tot['opex_var'] = tot['platform'] + tot['mgmt'] + tot['other']
    tot['fixed'] = tot['prop_tax'] + tot['strata'] + tot['insurance'] + tot['licence']
    tot['noi'] = tot['revenue'] - tot['opex_var'] - tot['fixed'] - tot['levy']
    tot['yield'] = tot['noi'] / tot['cost']
    return tot


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--data-dir', default='.'); ap.add_argument('--out-dir', default='results')
    args = ap.parse_args(); os.makedirs(args.out_dir, exist_ok=True)
    out = lambda n: os.path.join(args.out_dir, n)
    pd.options.display.float_format = '{:,.3f}'.format; pd.options.display.width = 220

    l = d.load_listings(d.find(args.data_dir, 'listings.csv.gz', 'listings_csv.gz', 'listings.csv'))
    a = d.analysis_set(l, [])
    rev = base_revenue(a)

    # ---------------- PART 3A: base case P&L ----------------
    rows = []
    for nb, (side, k) in AREAS.items():
        p = d.PRICE[(side, 'Condo')]; r = rev[nb]['base']
        cost = p + d.ptt(p) + d.SETUP['Condo'] + d.CLOSE
        noi = r * (1 - d.VAR) - p * d.PTAX - d.STRATA['Condo'] - d.INSURANCE['Condo'] - d.LICENCE
        rows.append(dict(area=nb, units=k, revenue_per_unit=r, all_in_cost_per_unit=cost, noi_per_unit=noi, yield_on_cost=noi / cost,
                         total_cost=cost * k, total_revenue=r * k, total_noi=noi * k))
    pnl = pd.DataFrame(rows)
    T = portfolio(rev)
    pnl.to_csv(out('part3_area_economics.csv'), index=False)
    lines = [('Gross revenue', T['revenue']), ('Platform fee (3%)', -T['platform']), ('Management (20%)', -T['mgmt']),
             ('Utilities, supplies, maintenance (15%)', -T['other']), ('Property tax (0.336% of price)', -T['prop_tax']),
             ('Strata fees', -T['strata']), ('Insurance', -T['insurance']), ('City STR licence', -T['licence']),
             ('Net operating income (NOI)', T['noi']), ('All in cost (price, transfer tax, setup, closing)', T['cost']),
             ('Net yield on cost', T['yield'])]
    pl = pd.DataFrame(lines, columns=['line', 'amount']); pl['share_of_revenue'] = pl.amount / T['revenue']
    pl.loc[pl.line.str.contains('yield|cost'), 'share_of_revenue'] = np.nan
    pl.to_csv(out('part3_base_case_pnl.csv'), index=False)
    print('PART 3A: base case P&L (13 condos)\n', pl.to_string(index=False)); print('\nBy area\n', pnl.to_string(index=False))
    print(f'Operating plus fixed costs as share of revenue: {(T["opex_var"] + T["fixed"]) / T["revenue"]:.1%}')

    # ---------------- PART 3B: cases ----------------
    cases = []
    for nm, sc in [('Low (25th percentile revenue)', 'p25'), ('Conservative (median)', 'median'), ('Base (capped mean)', 'base'), ('High (75th percentile)', 'p75')]:
        t = portfolio(rev, scenario=sc)
        cases.append(dict(case=nm, revenue=t['revenue'], noi=t['noi'], yield_on_cost=t['yield'], spread_over_policy_rate=t['yield'] - POLICY_RATE))
    C = pd.DataFrame(cases); C.to_csv(out('part3_cases.csv'), index=False); print('\nPART 3B: cases\n', C.to_string(index=False))

    # ---------------- PART 3C: monthly profile ----------------
    seas = pd.read_csv(out('seasonality.csv'))
    idx = seas.review_index.values; share = idx / idx.sum()
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    m = pd.DataFrame({'month': months, 'demand_index': idx, 'revenue': T['revenue'] * share})
    m['variable_costs'] = m.revenue * (T['opex_var'] / T['revenue']); m['fixed_costs'] = T['fixed'] / 12
    m['noi'] = m.revenue - m.variable_costs - m.fixed_costs; m['cumulative_noi'] = m.noi.cumsum()
    m.to_csv(out('part3_monthly_2027.csv'), index=False); print('\nPART 3C: monthly 2027\n', m.round(0).to_string(index=False))
    print(f'Summer (Jun to Aug) share of annual revenue: {share[5:8].sum():.1%}; lowest month NOI ${m.noi.min():,.0f}')

    # ---------------- PART 3D: sensitivity (tornado) ----------------
    base_y = T['yield']
    tests = [('Revenue per unit (minus 15% / plus 15%)', dict(rev_mult=.85), dict(rev_mult=1.15)),
             ('Management fee (25% / 15%)', dict(mgmt=.25), dict(mgmt=.15)),
             ('Utilities, supplies, maintenance (25% / 10%)', dict(other=.25), dict(other=.10)),
             ('Purchase price (plus 10% / minus 10%)', dict(price_mult=1.10), dict(price_mult=0.90)),
             ('Strata ($0.70 / $0.35 per sq ft)', dict(strata_sqft=.70), dict(strata_sqft=.35)),
             ('Insurance ($3,000 / $1,000)', dict(insurance=3000), dict(insurance=1000)),
             ('Furnishing ($20,000 / $5,000)', dict(setup=20000), dict(setup=5000))]
    S = []
    for nm, bad, good in tests:
        yb, yg = portfolio(rev, **bad)['yield'], portfolio(rev, **good)['yield']
        S.append(dict(driver=nm, yield_bad=yb, yield_base=base_y, yield_good=yg, swing=yg - yb))
    S = pd.DataFrame(S).sort_values('swing', ascending=False); S.to_csv(out('part3_sensitivity.csv'), index=False)
    print('\nPART 3D: sensitivity\n', S.to_string(index=False))

    # ---------------- PART 3E: break-even ----------------
    lo, hi = 0.0, 1.5
    for _ in range(60):
        mid = (lo + hi) / 2
        if portfolio(rev, rev_mult=mid)['noi'] > 0: hi = mid
        else: lo = mid
    be0 = hi
    lo, hi = 0.0, 3
    for _ in range(60):
        mid = (lo + hi) / 2
        if portfolio(rev, rev_mult=mid)['yield'] > POLICY_RATE: hi = mid
        else: lo = mid
    be_pol = hi
    nightly = {nb: a[(a.neighbourhood_cleansed == nb) & (a.seg == 'Condo')].price_num.median() for nb in AREAS}
    avg_price = sum(nightly[nb] * k for nb, (s, k) in AREAS.items()) / 13
    B = pd.DataFrame([dict(test='Revenue at which NOI = 0', revenue_multiplier=be0, revenue_per_unit=T['revenue'] / 13 * be0, booked_nights_at_median_price=T['revenue'] / 13 * be0 / avg_price),
                      dict(test='Revenue at which yield = policy rate (2.5%)', revenue_multiplier=be_pol, revenue_per_unit=T['revenue'] / 13 * be_pol, booked_nights_at_median_price=T['revenue'] / 13 * be_pol / avg_price),
                      dict(test='Base case', revenue_multiplier=1.0, revenue_per_unit=T['revenue'] / 13, booked_nights_at_median_price=T['revenue'] / 13 / avg_price)])
    B.to_csv(out('part3_breakeven.csv'), index=False); print('\nPART 3E: break-even (avg median nightly price $%.0f)\n' % avg_price, B.to_string(index=False))

    # ---------------- PART 3F: total return incl. price change (value moves with the purchase price, not setup or closing costs) ----------------
    price_value = sum(d.PRICE[(side, 'Condo')] * k for nb, (side, k) in AREAS.items())
    R = []
    for nm, g in [('Prices up 3%', .03), ('Prices flat', 0.0), ('Prices repeat last year (apartments minus 6.6%)', APT_PRICE_YOY), ('Prices minus 10%', -.10)]:
        for cs, sc in [('Conservative', 'median'), ('Base', 'base')]:
            t = portfolio(rev, scenario=sc)
            val = g * price_value
            R.append(dict(price_scenario=nm, income_case=cs, income_yield=t['yield'], value_change_dollars=val,
                          total_return_dollars=t['noi'] + val, total_return_pct_of_cost=(t['noi'] + val) / t['cost']))
    R = pd.DataFrame(R); R.to_csv(out('part3_total_return.csv'), index=False); print('\nPART 3F: total return\n', R.to_string(index=False))

    # ---------------- PART 4A: demand check (did the World Cup inflate revenue?) ----------------
    rv = d.read_any(d.find(args.data_dir, 'reviews.csv.gz', 'reviews_csv_1.gz', 'reviews_csv.gz', 'reviews.csv'), usecols=['listing_id', 'date'], parse_dates=['date'])
    est = a[pd.to_datetime(a.first_review) < '2025-01-01']
    tgt = est[(est.seg == 'Condo') & est.neighbourhood_cleansed.isin(AREAS)]
    rows = []
    for label, ids in [('All established listings in analysis set', est.id), ('Established condos in our 3 areas', tgt.id)]:
        x = rv[rv.listing_id.isin(ids)]
        g = x.groupby([x.date.dt.year, x.date.dt.month]).size().unstack(0)
        for mo in range(1, 9):
            rows.append(dict(group=label, month=mo, reviews_2025=g.loc[mo, 2025], reviews_2026=g.loc[mo, 2026], ratio=g.loc[mo, 2026] / g.loc[mo, 2025]))
    DM = pd.DataFrame(rows)
    tot = DM.groupby('group')[['reviews_2025', 'reviews_2026']].sum(); tot['ratio'] = tot.reviews_2026 / tot.reviews_2025
    summer = DM[DM.month.isin([6, 7])].groupby('group')[['reviews_2025', 'reviews_2026']].sum(); summer['ratio_jun_jul'] = summer.reviews_2026 / summer.reviews_2025
    DM.to_csv(out('part4_demand_check.csv'), index=False)
    print('\nPART 4A: Jan to Aug reviews 2026 vs 2025 (established listings)\n', tot.to_string(), '\nJune+July only (World Cup window)\n', summer.to_string())

    # ---------------- PART 4B: risk register (quantified) ----------------
    base_noi = T['noi']
    def row(rank, risk, like, yld, impact, kind, mit):
        return dict(rank=rank, risk=risk, likelihood=like, yield_if_it_happens=yld, change_vs_base_pts=(yld - base_y) * 100 if yld == yld else np.nan,
                    dollar_impact_per_year=impact, impact_type=kind, mitigation=mit)
    tp = portfolio(rev, levy=0.03); pv = portfolio(rev, price_mult=1.10)
    price_loss = -APT_PRICE_YOY * price_value
    risks = pd.DataFrame([
        row(1, 'Empty Homes Tax applies to short stay only units', 'Medium to high (City page: exempt only if rented 6+ months in 30+ day stays)', tp['yield'], base_noi - tp['noi'], 'lost net income',
            'Confirm with City of Vancouver before buying; test a mixed model with 30+ day stays 6+ months a year; if it applies, do not invest in the City'),
        row(2, 'Prices keep falling (apartments minus 6.6% year over year, Aug 2026)', 'High (down year over year in every 2026 report found)', (base_noi - price_loss) / T['cost'], price_loss, 'paper loss in property value',
            'Buy in tranches over 2 to 3 quarters; negotiate below benchmark; keep the reserve; judge the plan on income, not resale'),
        row(3, 'Revenue down 15% (weaker demand or new supply)', 'Medium', portfolio(rev, rev_mult=.85)['yield'], base_noi - portfolio(rev, rev_mult=.85)['noi'], 'lost net income',
            'Spread across 3 areas; dynamic pricing; hold the $464k reserve; stop rule if the first 6 months run below 85% of plan'),
        row(4, 'Operating costs higher than assumed (utilities, supplies, maintenance 25% not 15%)', 'Medium', portfolio(rev, other=.25)['yield'], base_noi - portfolio(rev, other=.25)['noi'], 'lost net income',
            'Get 3 management quotes and an insurance quote before closing; negotiate fee tiers'),
        row(5, 'Revenue estimate error (Inside Airbnb estimate; calendar check weak): low case', 'Medium', portfolio(rev, scenario='p25')['yield'], base_noi - portfolio(rev, scenario='p25')['noi'], 'lost net income',
            'Show the P25 to P75 range; validate with a local operator or paid market data before buying'),
        row(6, 'Purchase prices 10% above benchmark', 'Medium', pv['yield'], T['cost'] * 0.10 * price_value / T['cost'], 'extra cash needed (about 10% of price)',
            'Set a maximum price per unit; walk away above it'),
        row(7, 'Rules change or licence suspension (Vancouver counted 69 suspensions in Apr 2026)', 'Low to medium', np.nan, np.nan, 'cannot be sized from our data',
            'Licence and register every unit before listing; one named compliance owner; buildings whose bylaws allow short stays only')])
    risks.to_csv(out('part4_risk_register.csv'), index=False); print('\nPART 4B: risk register\n', risks[['rank', 'risk', 'yield_if_it_happens', 'change_vs_base_pts', 'dollar_impact_per_year', 'impact_type']].to_string(index=False))


if __name__ == '__main__':
    main()
