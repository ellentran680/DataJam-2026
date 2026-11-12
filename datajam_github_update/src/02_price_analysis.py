"""
02.py

Summarizes nightly prices and Inside Airbnb estimated annual revenue
for entire-home listings.

Input:  data/raw/listings.csv.gz
Output: outputs/property_type_price_revenue_summary.csv
        outputs/neighbourhood_price_revenue_summary.csv

Keep the raw dataset local; do not commit it to GitHub.
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "raw" / "listings.csv.gz"
OUTPUT = ROOT / "outputs"
OUTPUT.mkdir(parents=True, exist_ok=True)


def clean_currency(series):
    """Convert text prices such as '$125.00' into numbers."""
    cleaned = (
        series.astype("string")
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    return pd.to_numeric(cleaned, errors="coerce")


def summarize(data, group_column):
    return (
        data.groupby(group_column, dropna=False)
        .agg(
            listing_count=("property_type", "size"),
            median_nightly_price=("price_numeric", "median"),
            average_nightly_price=("price_numeric", "mean"),
            median_estimated_annual_revenue=(
                "estimated_revenue_l365d", "median"
            ),
            average_estimated_annual_revenue=(
                "estimated_revenue_l365d", "mean"
            ),
        )
        .reset_index()
        .sort_values("listing_count", ascending=False)
    )


def main():
    if not INPUT.exists():
        raise FileNotFoundError(
            f"Could not find dataset: {INPUT}\n"
            "Place listings.csv.gz inside data/raw/."
        )

    df = pd.read_csv(INPUT, low_memory=False)

    print("\nRevenue data quality check:")
    print("Total listings:", len(df))
    print("Missing revenue:", df["estimated_revenue_l365d"].isna().sum())

    revenue = pd.to_numeric(
        df["estimated_revenue_l365d"], errors="coerce"
    )

    print("Zero revenue:", (revenue == 0).sum())
    print("Negative revenue:", (revenue < 0).sum())

    required = [
        "room_type",
        "property_type",
        "neighbourhood_cleansed",
        "price",
        "estimated_revenue_l365d",
    ]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Analyze entire homes/apartments, not individual rooms.
    df = df.loc[df["room_type"].eq("Entire home/apt")].copy()

    df["price_numeric"] = clean_currency(df["price"])
    df["estimated_revenue_l365d"] = pd.to_numeric(
        df["estimated_revenue_l365d"], errors="coerce"
    )

    print("\nRevenue quality among entire-home listings:")
    print("Total:", len(df))
    print("Missing revenue:", df["estimated_revenue_l365d"].isna().sum())
    print("Zero revenue:", (df["estimated_revenue_l365d"] == 0).sum())
    print("Positive revenue:", (df["estimated_revenue_l365d"] > 0).sum())

    print("\nZero revenue by property type:")
    print(
        df.assign(
            zero_revenue=df["estimated_revenue_l365d"].eq(0)
        )
        .groupby("property_type")["zero_revenue"]
        .agg(["sum", "count"])
        .sort_values("sum", ascending=False)
        .to_string()
    )

    df["price_numeric"] = clean_currency(df["price"])
    df["estimated_revenue_l365d"] = pd.to_numeric(
        df["estimated_revenue_l365d"], errors="coerce"
    )

    # Keep only listings with positive estimated revenue
    # for the revenue-potential analysis.
    df = df.dropna(
        subset=[
            "property_type",
            "price_numeric",
            "estimated_revenue_l365d",
        ]
    )

    df = df[df["estimated_revenue_l365d"] > 0].copy()

    print(f"Positive-revenue listings analyzed: {len(df):,}")

    print(f"Entire-home listings analyzed: {len(df):,}")

    property_summary = summarize(df, "property_type")
    neighbourhood_summary = summarize(df, "neighbourhood_cleansed")

    property_summary.to_csv(
        OUTPUT / "property_type_price_revenue_summary.csv",
        index=False,
    )
    neighbourhood_summary.to_csv(
        OUTPUT / "neighbourhood_price_revenue_summary.csv",
        index=False,
    )

    print("\nPrice and revenue by property type:")
    print(property_summary.to_string(index=False))

    print("\nPrice and revenue by neighbourhood (first 15):")
    print(neighbourhood_summary.head(15).to_string(index=False))

    print(f"\nCSV summaries saved in: {OUTPUT}")


if __name__ == "__main__":
    main()
