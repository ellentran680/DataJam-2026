# DataJam 2026 — Vancouver Short-Term Rental Investment Case

**Repository:** [DataJam-2026](https://github.com/ellentran680/DataJam-2026)  
**Client:** Data-Driven Developments (DDD), fictional investment fund  
**Mandate:** Allocate CAD $10 million to BC short-term rental property for the case simulation.  
**Performance period:** January 1–December 31, 2027.

## 1. Current proposed investment recommendation

The team's working recommendation is a 13-condo portfolio within the City of Vancouver:

| Neighbourhood | Property type | Number of properties |
|---|---|---:|
| Downtown Eastside | Condo | 6 |
| Downtown | Condo | 5 |
| West End | Condo | 2 |
| **Total** | **Condos** | **13** |

The working allocation is based on the team's existing analysis and is a recommendation to be tested, not a claim that 13 specific properties have been purchased.

## 2. Property-type decision

The team's current decision is to prioritize condos and not to recommend houses or townhouses as the core portfolio. The working analysis reports the following median net yields on cost:

| Property type | Working median net yield |
|---|---:|
| Condo | 3.0% |
| Townhouse | 1.1% |
| House | 0.6% |

These are team-reported estimates. They must be reproducible from the analysis scripts and documented assumptions before being treated as final results.

**Important classification note:** Airbnb's `property_type` field is not necessarily equivalent to an investable strata condo. The analysis must document how raw categories are mapped to condo, house, townhouse, suite/guesthouse, and other. Do not assume that every `Entire rental unit` is a condo.

## 3. Data currently received

The uploaded files are:
- `listings.csv`
- `calendar.csv`
- `reviews.csv`

The current `listings.csv` inspected for this project contains 6,131 rows and 90 columns. Its `last_scraped` field indicates a September 2026 snapshot. The business-case brief specifies an Inside Airbnb snapshot dated June 15, 2026.

This date discrepancy must be disclosed and resolved with the team before final comparisons. The uploaded calendar starts in September 2026 and does not cover the full January–December 2027 calendar year. It cannot directly establish full-year 2027 occupancy.

Reviews are a proxy for guest activity, not a count of stays. Do not equate one review with one booking.

## 4. Location and listing-count outputs

The `outputs/` folder contains aggregate counts from the uploaded listings file:
- `raw_listings_by_neighbourhood.csv`
- `raw_listings_by_property_type.csv`
- `raw_listings_by_room_type.csv`

These are raw snapshot counts, not filtered investment-eligible counts. The cleaning pipeline must separately report how each filter changes the sample.

## 5. Reproducibility

Create a Python environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\\Scripts\\activate   # Windows

pip install -r requirements.txt
python src/01_listing_summary.py
```

The script reads the raw listings file from `data/raw/listings.csv` and writes only aggregate, non-identifying outputs to `outputs/`.

Do not commit raw Airbnb files. They can contain host, listing, reviewer, or other identifying information. Keep raw files locally and use `.gitignore`.

## 6. Data sources and citations

### Case-provided sources
- Business Case Brief, *The Airbnb Vancouver Problem*, SFU DSSS DataJam 2026 (user-provided project brief).
- Inside Airbnb, Vancouver data: https://insideairbnb.com/get-the-data/
- Data credit required by the case: **Data: Inside Airbnb, Vancouver, 15 June 2026, CC BY 4.0.**

### External sources to validate assumptions
- Greater Vancouver REALTORS, August 2026 market information: https://www.gvrealtors.ca/news/home-sales-continue-downward-trend-to-close-the-summer
- BC Property Transfer Tax: https://www2.gov.bc.ca/gov/content/taxes/property-taxes/property-transfer-tax
- City of Vancouver short-term rentals: https://vancouver.ca/doing-business/short-term-rentals.aspx
- City of Vancouver Empty Homes Tax: https://vancouver.ca/home-property-development/empty-homes-tax.aspx
- BC Short-Term Rental Accommodations Act information: https://www2.gov.bc.ca/gov/content/housing-tenancy/short-term-rentals
- Canada Revenue Agency, GST/HST and platform economy: https://www.canada.ca/en/revenue-agency/programs/about-canada-revenue-agency/compliance/platform-economy/sharing-economy.html

**Source discipline:** Record the exact page/document, publication or effective date, access date, assumption used, and reliability. Recheck all tax, fee, and regulatory rates for the 2027 operating year before finalizing the model.

## 7. Limitations and open questions

1. The case simulation waives the principal-residence requirement only. Other legal requirements remain relevant to the simulation.
2. Real-world legality and case-simulation assumptions must be presented separately.
3. The listing snapshot is not an official or complete census of short-term rentals.
4. Calendar unavailability can mean booked or blocked; it is not equivalent to confirmed occupancy.
5. Inside Airbnb estimated occupancy and revenue are estimates, not reported financial results.
6. Area-wide benchmark prices are not property-specific purchase prices.
7. Tax treatment depends on ownership structure, assessed value, exemptions, and actual use.
8. The team's 2027 revenue, operating cost, and net-yield estimates are projections, not realized results.

## 8. Planned analysis modules

| Module | Purpose |
|---|---|
| `01_listing_summary.py` | Raw listing counts by neighbourhood and property type |
| `02_data_cleaning.py` | Cleaning, eligibility filters, and filter audit |
| `03_revenue_analysis.py` | Revenue, price, occupancy, and review analysis |
| `04_location_analysis.py` | Neighbourhood comparison |
| `05_financial_model.py` | Acquisition cost, operating expenses, NOI, yield |
| `06_sensitivity_analysis.py` | Revenue, price, fee, and tax stress tests |
| `07_risk_analysis.py` | Risk register and quantified exposures |
| `08_portfolio_simulation.py` | Portfolio uncertainty and correlated market shocks |

## 9. Privacy

Do not publish host names, host IDs, reviewer names, reviewer IDs, listing URLs, real licence numbers, or row-level records. Publish aggregate tables and charts only.
