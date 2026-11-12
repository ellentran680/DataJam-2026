# DDD $10M case

Data: Inside Airbnb, Vancouver, CC BY 4.0. The files given are dated 2026-09-17 (the brief says June 15).

---------------------------------------------------------------------

## PART A: Run the analysis

### Step 1. Install Python (skip if you already have it)
1. Go to https://www.python.org/downloads/ and download the newest Python 3.
2. Run the installer. IMPORTANT: tick the box "Add python.exe to PATH" on the first screen, then click Install.
3. Check it worked: press the Windows key, type cmd, open "Command Prompt", type:  py --version
   You should see something like Python 3.12.x. (Mac: open Terminal and type python3 --version)

### Step 2. Unzip the package
1. Find DDD_package.zip in your Downloads. Right click, Extract All.
2. You get a folder called DDD_package. Move it somewhere easy, for example C:\DDD_package (Mac: your Documents folder).

### Step 3. Put the Inside Airbnb data in a folder
1. Make a folder called C:\DDD_data (Mac: Documents/DDD_data).
2. Put the three Vancouver files inside it. Do NOT unzip the .gz files, the script reads them as they are.
3. Rename them exactly (the script looks for these names):
   - listings.csv.gz
   - calendar.csv.gz
   - reviews.csv.gz
   (If yours are called listings_csv.gz, calendar_csv_1.gz and reviews_csv_1.gz, those work too.)
   If your names have extra bits like "(1)", rename them.

### Step 4. Open a terminal inside the package folder
1. Open File Explorer and go into C:\DDD_package.
2. Click the address bar at the top, type cmd, press Enter. A black window opens already inside that folder.
   (Mac: open Terminal, type  cd ~/Documents/DDD_package  and press Enter.)

### Step 5. Install the helper libraries (once only)
Copy this line into the black window and press Enter:

    python -m pip install -r requirements.txt   (if that fails, use: py -m pip install -r requirements.txt)

(Mac: python3 -m pip install -r requirements.txt)
Wait until it finishes. Lots of text is normal.

### Step 6. Run the analysis
Your data files (listings, calendar, reviews) are sitting inside the DDD_package folder, and your PowerShell window is already in that folder, so use this exact command (the dot means "this folder"):

    python code\ddd_analysis.py --data-dir "." --out-dir results

If Windows says python is not recognized, try the same line starting with py instead:

    py code\ddd_analysis.py --data-dir "." --out-dir results

Notes for your laptop:
- Windows hides the ".gz" ending, so listings.csv in File Explorer is really listings.csv.gz (the WinRAR icon shows it is compressed). Leave the three files as they are, do not unzip them.
- If your data is in a different folder, put its full path in quotes instead of the dot, for example --data-dir "C:\Users\hoamy\Downloads\data".
- The yellow PATH warning during the install is harmless, ignore it.
- It takes about 1 to 3 minutes. Text scrolls past. When you can type again, it worked.
- Mac: python3 code/ddd_analysis.py --data-dir . --out-dir results

### Step 6b. Verify the data first (recommended, 1 minute)
Before or after Step 6, run this to prove the files are the right city and are clean:

    python code\verify_data.py --data-dir "." --out-dir results

You should see about 18 PASS, 3 WARN and 0 FAIL, ending with "DATA OK TO USE". The 3 WARN lines are normal (snapshot date is not June 15, 15.8% of listings have no price, 13% sit at the 255 night cap), so mention them as data limitations. A FAIL means stop: for example the wrong city or the small summary file. It also checks that your numbers match ours (6,131 listings, 2,702 in the analysis set, $9,535,818 for the 13 condos). A report is saved in results\verification_report.csv.


### Step 7. Check your numbers match (this is your proof it is correct)
Scroll up in the black window and look for these lines. They should be the same or within about 0.1 point on the simulated ones:

- Listings loaded: 6131; entire homes 5012
- Filter steps ending with 2702 listings and median revenue about 41,511
- Analysis set by type: Condo 1030, House 1000, Townhouse 44
- Condo yield by area: Downtown Eastside 3.5%, Downtown 3.3%, West End 3.1%
- Property types: Condo median yield 3.0%, Townhouse 1.1%, House 0.6%
- Last line: Recommended 13 condos: all in cost $9,535,818; unspent $464,182

If they match, you have reproduced the whole analysis.

### Step 8. Open your results
Open the new folder DDD_package\results. Each .csv file opens in Excel. The table at the bottom of this guide says which file answers which question.

### Step 9. (Optional) Make the slide charts and the workbook again
Charts (still in the same black window):

    python code\make_charts.py results charts

Workbook for Ellen:

    cd results
    python ..\code\build_workbook.py

This makes DDD_handoff_workbook.xlsx inside results. Open it in Excel and let it calculate. (The ready made copy is already in the workbook folder, so you only need this if you change an assumption.)

### Step 9b. Part 3 and Part 4 numbers (Ellen and the risk person)
After Step 6 has finished, run this in the same black window:

    python code\ddd_part3_part4.py --data-dir "." --out-dir results

It prints the base case profit and loss, the four cases, monthly 2027 cash flow, sensitivity, break even, total return with price changes, the World Cup demand check and the ranked risk register, and saves each as a CSV in results (names start with part3_ and part4_). To add them to the Excel file as extra sheets:

    python code\add_part3_part4_sheets.py results workbook\DDD_handoff_workbook.xlsx

(The package workbook already has these sheets. Only rerun if you change an assumption.)

---------------------------------------------------------------------

## PART B: How to use the results for your slides and Q&A

### Your three slides (plus one appendix slide)
1. Location (Part 1): use charts/chart_location_condo_yield.png and the area table from results/location_evidence.csv. Message: Downtown Eastside, Downtown and West End win because they have the most booked nights (144 a year) and the best yield.
2. Property types (Part 2): use charts/chart_type_yield.png and results/property_type_comparison.csv. Message: condos earn about $62 of revenue per $1,000 invested, houses about $22.
3. How many (Part 2): use results/how_many_vs_spread.csv and results/portfolio_compare.csv. Message: the expected yield stays near 3.7% whether you buy 3 or 13, but the range narrows from 1.5% to 5.9% down to 2.7% to 4.7%.
4. Appendix: your three decision log entries (see the Parts 1 and 2 doc, section 7), with results/decision1_filter_steps.csv as evidence.
Also put somewhere in the deck: "Data: Inside Airbnb, Vancouver, CC BY 4.0" and a line saying AI was used and how you checked it (you ran the script and matched the numbers).

### Before you present, do these two checks
1. Open the REBGV Vancouver East and Vancouver West reports and confirm the six benchmark prices listed in SOURCES.md, item 1.
2. Open vancouver.ca (Empty Homes Tax page) and confirm the rate and the exemption rule, SOURCES.md item 4.

### Practice answering these out loud (full answers are in the Parts 1 and 2 doc, section 9)
- Where does the revenue number come from, and how do you know it is reasonable?
- Why condos and not houses?
- Why 13 properties?
- What is the biggest risk?
- Where do your cost assumptions come from?
Never say "the model chose that". Say what you decided, why, and what it changed.

---------------------------------------------------------------------

## Which file answers which question

| File | Use it when a judge asks |
|---|---|
| code/ddd_analysis.py | Trace any number to a line of code. Cost assumptions are at the top, each with a source note |
| code/build_workbook.py | How the Excel handoff was made |
| code/make_charts.py | How the slide charts were made |
| SOURCES.md | Where does each price, rate and cost come from? |
| results/decision1_filter_steps.csv | What did each cleaning step do? (Decision 1) |
| results/validation_checks.csv | How do you know revenue is reasonable? (calendar check, 255 night cap) |
| results/location_evidence.csv | Why this area and not another? (Part 1) |
| results/yield_by_segment.csv | Yield by area and type with ranges |
| results/price_sensitivity.csv | What if purchase prices are higher than the benchmark? |
| results/property_type_comparison.csv | Why condos, not houses or townhouses? (Part 2) |
| results/how_many_vs_spread.csv | Why 13 properties? |
| results/portfolio_compare.csv | 13 condos versus 3 houses versus 5 houses |
| results/scenarios.csv | Stress cases: revenue down, costs up, tax |
| results/concentration_test.csv | Why spread across three areas? |
| results/seasonality.csv | Monthly demand pattern |
| code/ddd_part3_part4.py | Part 3 (expected performance) and Part 4 (risk) numbers |
| results/part3_*.csv | Base case P&L, cases, monthly 2027, sensitivity, break even, total return |
| results/part4_*.csv | World Cup demand check and the ranked risk register |
| charts/chart_part3_*.png | Sensitivity and monthly charts for Part 3 slides |
| workbook/DDD_handoff_workbook.xlsx | Part 3 inputs: live formulas, scenarios, Sources sheet |
| charts/*.png | Slide charts |

## Headline
13 condos (6 Downtown Eastside, 5 Downtown, 2 West End), all in cost $9,535,818, unspent $464,182. Base 2027 net yield about 3.7% (about 2.7% to 4.8%). Houses 0.6%, townhouses 1.1% median yield. A 3% of value annual levy (Empty Homes Tax) would cut yield to about 0.8%.
