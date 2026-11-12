"""
01_listing_summary.py

Creates aggregate, non-identifying counts from the uploaded listings.csv.
Raw input stays local; only aggregate CSV outputs are written.
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "raw" / "listings.csv"
OUTPUT = ROOT / "outputs"
OUTPUT.mkdir(parents=True, exist_ok=True)

def export_counts(df: pd.DataFrame, column: str, filename: str) -> None:
    counts = (
        df[column]
        .fillna("Unknown")
        .value_counts(dropna=False)
        .rename_axis(column)
        .reset_index(name="listing_count")
    )
    counts.to_csv(OUTPUT / filename, index=False)
    print(f"\n{column}:")
    print(counts.to_string(index=False))

def main() -> None:
    if not INPUT.exists():
        raise FileNotFoundError(
            f"Place listings.csv at: {INPUT}\n"
            "Do not commit this raw file to GitHub."
        )

    df = pd.read_csv(INPUT, low_memory=False)
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    required = [
        "neighbourhood_cleansed",
        "property_type",
        "room_type",
    ]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")

    export_counts(
        df, "neighbourhood_cleansed",
        "raw_listings_by_neighbourhood.csv"
    )
    export_counts(
        df, "property_type",
        "raw_listings_by_property_type.csv"
    )
    export_counts(
        df, "room_type",
        "raw_listings_by_room_type.csv"
    )

if __name__ == "__main__":
    main()
