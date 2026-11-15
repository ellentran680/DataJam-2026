# DDD $10M Vancouver Investment Case

## Project overview

This project evaluates a hypothetical $10 million investment in short-term rental properties in Vancouver, British Columbia.

The analysis compares neighbourhoods and property types, evaluates portfolio diversification, and estimates operating yields under different assumptions.

**Recommendation:** 13 condos:
- 6 in Downtown Eastside
- 5 in Downtown
- 2 in West End

| Portfolio metric | Result |
|---|---:|
| Total all-in cost | $9,535,818 |
| Unspent budget | $464,182 |
| Base-case median net yield | 2.7% |
| Simulated P10–P90 yield range | 1.9%–3.5% |

These are model estimates, not guaranteed investment returns.

## 1. Data and limitations

**Source:** Inside Airbnb, Vancouver, CC BY 4.0.

The case brief specifies a June 15, 2026 data snapshot. However, the dataset available for this project is dated September 17–18, 2026. This discrepancy is disclosed rather than treated as equivalent to the requested snapshot.

The repository includes:
- `listings.csv.gz`
- `calendar.csv.gz`
- `reviews.csv.gz`
- `neighbourhoods.geojson`

Important limitations:
- Airbnb estimated revenue is not audited or guaranteed income.
- Calendar-unavailable dates may represent bookings or host-blocked dates.
- Reviews are an imperfect proxy for completed stays.
- The model's occupancy and revenue estimates depend on the available snapshot and its assumptions.
- The analysis does not establish that a specific property is legally eligible for short-term rental operation.

## 2. Financial assumptions

The current model uses a **50.5% variable-cost assumption**:
- 15.5% Airbnb host-fee assumption
- 20% property management
- 15% utilities, supplies, and maintenance

The 15.5% host fee is an assumption for the applicable host fee structure, not a universal fee for every Airbnb host. Actual fees and account structures should be verified before an acquisition.

Other assumptions, including property taxes, strata fees, insurance, furnishing, closing costs, and licensing, are documented in the workbook's `Assumptions` and `Sources` sheets.

The base-case yield is lower than the earlier 3.7% estimate because the updated model uses the 50.5% variable-cost assumption.

## 3. Key results

Recommended portfolio: 13 condos:
- 6 Downtown Eastside
- 5 Downtown
- 2 West End

Total all-in cost: $9,535,818.
Unspent budget: $464,182.
Base-case median net yield: 2.7%.
Simulated P10–P90 yield range: 1.9%–3.5%.

Neighbourhood median net yields:
- Downtown Eastside: approximately 2.5%
- Downtown: approximately 2.4%
- West End: approximately 2.2%

## 4. Limitations and responsible use

Airbnb estimated revenue is not audited income. Calendar-unavailable dates may represent bookings or host blocks, and reviews are an imperfect proxy for completed stays.

The case brief specifies a June 15, 2026 data snapshot. The available dataset is dated September 17–18, 2026. This discrepancy should be considered when interpreting the results.

The model assumes 50.5% variable costs: a 15.5% Airbnb host-fee assumption, 20% management, and 15% utilities, supplies, and maintenance. Actual fees and operating costs may differ.

The principal-residence requirement is set aside for this hypothetical simulation. This does not establish legal eligibility for any real property.

Before an actual acquisition, independently verify licensing, provincial registration, strata restrictions, fees, taxes, and operating costs.

