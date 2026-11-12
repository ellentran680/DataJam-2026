"""
03_financial_model.py

Builds a transparent, assumption-based operating model for Vancouver
short-term-rental property-type proxies.

INPUT
    data/raw/listings.csv.gz

OUTPUT
    outputs/financial_model_by_asset_type.csv
    outputs/financial_model_sensitivity.csv

IMPORTANT MODEL LIMITATIONS
- Inside Airbnb estimated revenue is a listing-level estimate, not audited income.
- Only entire-home listings with positive estimated revenue are used for
  the revenue medians. This is a selected sample and may overstate typical
  revenue across all listings.
- "Entire home" is used only as a rough HOUSE proxy.
- "Entire condo" and "Entire townhouse" are listing property-type proxies;
  they do not prove the underlying legal/strata asset classification.
- Purchase-price benchmarks and operating-cost assumptions below are
  illustrative inputs. Verify/update them with primary sources before
  presenting the results.
- The model excludes financing costs and income tax.
- The 38% variable operating-cost assumption is a placeholder. In
  particular, verify the platform fee and management arrangement before
  relying on the result.

Run from the project root:
    python3 src/03_financial_model.py
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "raw" / "listings.csv.gz"
OUTPUT = ROOT / "outputs"
OUTPUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------
# MODEL ASSUMPTIONS — edit these when you have verified sources.
# All amounts are CAD.
# ---------------------------------------------------------------------

VARIABLE_OPERATING_COST_RATE = 0.505  # placeholder: share of gross revenue
PROPERTY_TAX_RATE = 0.00336394       # 2026 proxy; verify 2027 rate
ANNUAL_BUSINESS_LICENCE = 1108       # verify current City fee
CLOSING_COST = 4000                 # illustrative estimate

# Purchase price benchmarks and fixed annual costs.
# These are assumptions, not values read from the Airbnb dataset.
ASSET_ASSUMPTIONS = {
    "Condo": {
        "listing_property_type": "Entire condo",
        "purchase_price": 774900,
        "setup_cost": 10000,
        "annual_strata": 3780,
        "annual_insurance": 2000,
    },
    "Townhouse": {
        "listing_property_type": "Entire townhouse",
        "purchase_price": 1334900,
        "setup_cost": 15000,
        "annual_strata": 3780,
        "annual_insurance": 2500,
    },
    "House (proxy)": {
        "listing_property_type": "Entire home",
        "purchase_price": 2932700,
        "setup_cost": 20000,
        "annual_strata": 0,
        "annual_insurance": 3000,
    },
}

# Property transfer tax estimate for ordinary residential transfers.
# This function does not include exemptions, additional property taxes,
# GST, foreign-buyer tax, or other special circumstances.
def estimate_property_transfer_tax(price: float) -> float:
    tax = 0.0
    tax += min(price, 200_000) * 0.01
    tax += max(min(price, 2_000_000) - 200_000, 0) * 0.02
    tax += max(min(price, 3_000_000) - 2_000_000, 0) * 0.03
    tax += max(price - 3_000_000, 0) * 0.05
    return tax


def load_positive_revenue_listings() -> pd.DataFrame:
    if not INPUT.exists():
        raise FileNotFoundError(
            f"Could not find {INPUT}. Place listings.csv.gz in data/raw/."
        )

    df = pd.read_csv(INPUT, low_memory=False)

    required = [
        "room_type",
        "property_type",
        "price",
        "estimated_revenue_l365d",
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df.loc[df["room_type"].eq("Entire home/apt")].copy()
    df["estimated_revenue_l365d"] = pd.to_numeric(
        df["estimated_revenue_l365d"], errors="coerce"
    )

    # Revenue medians use positive-revenue listings only.
    df = df.loc[df["estimated_revenue_l365d"] > 0].copy()
    return df


def build_asset_model(df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for asset_name, assumptions in ASSET_ASSUMPTIONS.items():
        property_type = assumptions["listing_property_type"]
        segment = df.loc[df["property_type"].eq(property_type)]

        if segment.empty:
            print(f"WARNING: No positive-revenue listings for {property_type}")
            continue

        revenue_median = float(segment["estimated_revenue_l365d"].median())
        revenue_mean = float(segment["estimated_revenue_l365d"].mean())

        purchase = assumptions["purchase_price"]
        ptt = estimate_property_transfer_tax(purchase)
        setup = assumptions["setup_cost"]
        all_in_cost = purchase + ptt + setup + CLOSING_COST

        variable_costs = revenue_median * VARIABLE_OPERATING_COST_RATE
        property_tax = purchase * PROPERTY_TAX_RATE
        licence = ANNUAL_BUSINESS_LICENCE
        strata = assumptions["annual_strata"]
        insurance = assumptions["annual_insurance"]

        annual_fixed_costs = property_tax + licence + strata + insurance
        noi = revenue_median - variable_costs - annual_fixed_costs
        yield_pct = noi / all_in_cost * 100

        rows.append({
            "asset_type_proxy": asset_name,
            "source_listing_property_type": property_type,
            "positive_revenue_listing_count": len(segment),
            "median_estimated_annual_revenue": revenue_median,
            "average_estimated_annual_revenue": revenue_mean,
            "purchase_price_assumption": purchase,
            "estimated_property_transfer_tax": ptt,
            "setup_cost_assumption": setup,
            "closing_cost_assumption": CLOSING_COST,
            "all_in_acquisition_cost": all_in_cost,
            "variable_operating_cost_rate": VARIABLE_OPERATING_COST_RATE,
            "estimated_variable_operating_cost": variable_costs,
            "estimated_property_tax": property_tax,
            "annual_business_licence": licence,
            "annual_strata": strata,
            "annual_insurance": insurance,
            "estimated_annual_noi": noi,
            "net_operating_yield_pct": yield_pct,
        })

    return pd.DataFrame(rows)


def build_sensitivity(model: pd.DataFrame) -> pd.DataFrame:
    rows = []
    revenue_multipliers = {
        "Downside: revenue -20%": 0.80,
        "Base case": 1.00,
        "Upside: revenue +10%": 1.10,
    }

    for _, item in model.iterrows():
        for scenario, multiplier in revenue_multipliers.items():
            revenue = item["median_estimated_annual_revenue"] * multiplier
            variable_cost = revenue * VARIABLE_OPERATING_COST_RATE
            fixed_costs = (
                item["estimated_property_tax"]
                + item["annual_business_licence"]
                + item["annual_strata"]
                + item["annual_insurance"]
            )
            noi = revenue - variable_cost - fixed_costs
            yield_pct = noi / item["all_in_acquisition_cost"] * 100

            rows.append({
                "asset_type_proxy": item["asset_type_proxy"],
                "scenario": scenario,
                "annual_revenue": revenue,
                "annual_operating_costs": variable_cost + fixed_costs,
                "annual_noi": noi,
                "all_in_acquisition_cost": item["all_in_acquisition_cost"],
                "net_operating_yield_pct": yield_pct,
            })

    return pd.DataFrame(rows)


def main():
    df = load_positive_revenue_listings()
    print(f"Positive-revenue entire-home listings loaded: {len(df):,}")

    model = build_asset_model(df)
    if model.empty:
        raise ValueError("No asset-type groups matched the configured proxies.")

    sensitivity = build_sensitivity(model)

    model_path = OUTPUT / "financial_model_by_asset_type.csv"
    sensitivity_path = OUTPUT / "financial_model_sensitivity.csv"

    model.to_csv(model_path, index=False)
    sensitivity.to_csv(sensitivity_path, index=False)

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 180)

    print("\nFinancial model by asset type:")
    print(model.round(2).to_string(index=False))

    print("\nRevenue sensitivity:")
    print(sensitivity.round(2).to_string(index=False))

    print("\nFiles saved:")
    print(model_path)
    print(sensitivity_path)

    print(
        "\nReminder: these are illustrative screening estimates, not "
        "investment-grade forecasts. Verify every assumption and confirm "
        "the asset-type proxies before using the results."
    )


if __name__ == "__main__":
    main()
