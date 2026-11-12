"""
04_portfolio_allocation.py

Uses the output from 03_financial_model.py to compare whole-property
portfolio combinations under a CAD $10 million budget.

INPUT
    outputs/financial_model_by_asset_type.csv

OUTPUT
    outputs/portfolio_allocation_ranked.csv
    outputs/portfolio_allocation_summary.csv

The script reports:
1. The highest-NOI portfolio with no diversification requirement.
2. The highest-NOI portfolio containing at least one condo, townhouse,
   and house-proxy property.
3. The 20 highest-NOI diversified combinations.

IMPORTANT
- This is a simplified screening model, not a full portfolio optimizer.
- It assumes each property's revenue and costs equal the asset-type
  median-based estimates in Script 03.
- It does not model correlated market risk, financing, tax on income,
  resale value, transaction timing, or property-specific differences.
- "Entire home" is only a rough house proxy.
- A minimum of one property in each category is an illustrative
  diversification rule, not a case requirement.
- Update the budget below if the case rules change.

Run from the project root:
    python3 src/04_portfolio_allocation.py
"""

from pathlib import Path
from itertools import product
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "outputs" / "financial_model_by_asset_type.csv"
OUTPUT = ROOT / "outputs"
OUTPUT.mkdir(parents=True, exist_ok=True)

BUDGET = 10_000_000
TOP_N = 20


def main():
    if not INPUT.exists():
        raise FileNotFoundError(
            f"Missing {INPUT}. Run 03_financial_model.py first."
        )

    model = pd.read_csv(INPUT)

    required = [
        "asset_type_proxy",
        "all_in_acquisition_cost",
        "estimated_annual_noi",
        "net_operating_yield_pct",
    ]
    missing = [c for c in required if c not in model.columns]
    if missing:
        raise ValueError(f"Missing columns in financial model: {missing}")

    # Stable order for readable output.
    model = model.set_index("asset_type_proxy").loc[
        ["Condo", "Townhouse", "House (proxy)"]
    ].reset_index()

    names = model["asset_type_proxy"].tolist()
    costs = model["all_in_acquisition_cost"].tolist()
    nois = model["estimated_annual_noi"].tolist()

    # Enumerate feasible whole-property combinations.
    max_counts = [
        int(BUDGET // cost) for cost in costs
    ]

    portfolios = []
    for counts in product(*(range(n + 1) for n in max_counts)):
        total_cost = sum(count * cost for count, cost in zip(counts, costs))
        if total_cost > BUDGET:
            continue

        total_noi = sum(count * noi for count, noi in zip(counts, nois))
        invested_yield = (
            total_noi / total_cost * 100 if total_cost > 0 else 0.0
        )
        remaining_cash = BUDGET - total_cost

        row = {
            "condo_count": counts[0],
            "townhouse_count": counts[1],
            "house_proxy_count": counts[2],
            "total_properties": sum(counts),
            "total_acquisition_cost": total_cost,
            "remaining_cash": remaining_cash,
            "estimated_annual_noi": total_noi,
            "portfolio_yield_on_invested_capital_pct": invested_yield,
            "budget_utilization_pct": total_cost / BUDGET * 100,
        }
        portfolios.append(row)

    results = pd.DataFrame(portfolios)

    # No diversification constraint: pure maximum estimated NOI.
    unconstrained = results.sort_values(
        ["estimated_annual_noi", "remaining_cash"],
        ascending=[False, True],
    ).iloc[0]

    # Illustrative diversification constraint: at least one of each type.
    diversified = results.loc[
        (results["condo_count"] >= 1)
        & (results["townhouse_count"] >= 1)
        & (results["house_proxy_count"] >= 1)
    ].copy()

    if diversified.empty:
        raise ValueError(
            "No portfolio containing at least one of each asset type "
            "fits within the budget."
        )

    diversified = diversified.sort_values(
        ["estimated_annual_noi", "remaining_cash"],
        ascending=[False, True],
    )

    ranked_path = OUTPUT / "portfolio_allocation_ranked.csv"
    diversified.head(TOP_N).to_csv(ranked_path, index=False)

    summary = pd.DataFrame([
        {
            "portfolio_rule": "Maximum estimated NOI; no diversification constraint",
            **unconstrained.to_dict(),
        },
        {
            "portfolio_rule": "Maximum estimated NOI; at least one of each asset type",
            **diversified.iloc[0].to_dict(),
        },
    ])

    summary_path = OUTPUT / "portfolio_allocation_summary.csv"
    summary.to_csv(summary_path, index=False)

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 180)

    print(f"Budget: ${BUDGET:,.0f}")
    print("\nBest portfolio under each rule:")
    print(summary.round(2).to_string(index=False))

    print(f"\nTop {min(TOP_N, len(diversified))} diversified portfolios:")
    print(diversified.head(TOP_N).round(2).to_string(index=False))

    print("\nFiles saved:")
    print(summary_path)
    print(ranked_path)

    print(
        "\nInterpretation: the unconstrained result maximizes modeled NOI "
        "only. The diversified result uses an illustrative one-of-each "
        "rule. Neither result accounts for correlated risks or property-level "
        "variation."
    )


if __name__ == "__main__":
    main()
