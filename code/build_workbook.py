import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
F=lambda **k: Font(name='Arial',size=10,**k)
BLUE=F(color='0000FF'); BLK=F(); BOLD=F(bold=True); GRN=F(color='008000')
YEL=PatternFill('solid',fgColor='FFFF00'); HDR=PatternFill('solid',fgColor='D9E1F2')
wb=Workbook()
def hdr(ws,row,vals):
    for i,v in enumerate(vals,1):
        c=ws.cell(row=row,column=i,value=v); c.font=BOLD; c.fill=HDR; c.alignment=Alignment(wrap_text=True,vertical='top')
# ---------- README
ws=wb.active; ws.title='README'
lines=["DDD $10M short term rental case: handoff workbook for financial analysis",
"Blue text = hardcoded input (edit these). Black = formula. Green = link to another sheet. Yellow fill = key lever.",
"Sheets: Assumptions (all inputs), Sources (where every number comes from), Portfolio (13 condo recommendation with formulas), Alternatives (houses, townhouses, few vs many), Location_evidence, Seasonality.",
"Revenue inputs come from Inside Airbnb Vancouver (listings.csv.gz): estimated_revenue_l365d for entire homes, min nights <=29, city+provincial licence numbers, active, price within P1 to P99. Data: Inside Airbnb, Vancouver, CC BY 4.0. Snapshot file is dated 2026-09-17.",
"Purchase prices: REBGV benchmark prices, Aug 2026 (see Sources). Cost assumptions are now each tied to a source on the Sources sheet; the weakest are insurance and the 15% utilities, supplies and maintenance share.",
"Pre income tax, all cash, no appreciation, assessed value assumed equal to benchmark price.",
"Revenue scenarios per listing: Low = 25th percentile, Conservative = median, Base = mean after capping at 95th percentile, High = 75th percentile of listings in that area and type.",
"Code that produced the data inputs: 01 to 07 .py scripts in the repo."]
for i,t in enumerate(lines,1):
    ws.cell(row=i,column=1,value=t).font=BOLD if i==1 else BLK
ws.column_dimensions['A'].width=150
# ---------- Assumptions
A=wb.create_sheet('Assumptions')
A['A1']='Assumptions'; A['A1'].font=BOLD
hdr(A,2,['Item','Value','Unit','Source / note'])
rows=[('Budget',10000000,'$','DDD mandate (case brief)'),
('Variable costs share of revenue',0.38,'% revenue','3% platform fee + 20% management + 15% utilities, supplies, maintenance. See Sources sheet, items 6 to 8'),
('Property tax rate',0.00336394,'% of price','City of Vancouver 2026 Class 1 residential total rate $3.36394 per $1,000 (Sources item 9). Assumes assessed value equals benchmark price'),
('Condo strata fees',3780,'$/yr','$0.525 per sq ft per month (midpoint of Vancouver $0.35 to $0.70) x 600 sq ft x 12 (Sources item 10)'),
('Condo insurance',2000,'$/yr','Short term rental policy; US examples $2,200 to $3,200 for 3+ bedroom homes, so weakest evidence (Sources item 12)'),
('Condo furnishing and setup',10000,'$/unit','Airbtics Canada 1BR $4,829; quality 1BR $7,500 to $12,500; Awning $10,000 to $30,000 (Sources item 13)'),
('Legal, title insurance, inspection, adjustments',4000,'$/unit','Worked example for a $900k Greater Vancouver purchase totals $3,850 (Sources item 14)'),
('Revenue shock (stress lever)',0.0,'%','Set -0.15 for revenue down 15%'),
('Extra annual levy (stress lever)',0.0,'% of price','Set 0.03 to test the Empty Homes Tax (3% of assessed value for properties not rented 6+ months in 30+ day periods) (Sources item 4)'),
('East side condo benchmark price',628600,'$','REBGV Vancouver East condo benchmark, Aug 2026 (Sources item 1)'),
('West side condo benchmark price',774900,'$','REBGV Vancouver West condo benchmark, Aug 2026 (Sources item 1)'),
('City of Vancouver STR business licence',1108,'$/yr','Official fee $1,108 per year (+$77 first application) (Sources item 5)')]
for r,(a,b,c,d) in enumerate(rows,3):
    A.cell(row=r,column=1,value=a).font=BLK
    x=A.cell(row=r,column=2,value=b); x.font=BLUE
    if c.startswith('%'): x.number_format='0.0%'
    else: x.number_format='$#,##0'
    A.cell(row=r,column=3,value=c).font=BLK; A.cell(row=r,column=4,value=d).font=BLK
for r in (10,11): A.cell(row=r,column=2).fill=YEL
A['A15']='BC property transfer tax brackets (applied in Portfolio)'; A['A15'].font=BOLD
for r,(t,v) in enumerate([('1% up to $200,000',0.01),('2% from $200,000 to $2,000,000',0.02),('3% from $2,000,000 to $3,000,000',0.03),('5% above $3,000,000',0.05)],16):
    A.cell(row=r,column=1,value=t).font=BLK; c=A.cell(row=r,column=2,value=v); c.font=BLUE; c.number_format='0%'
for col,w in zip('ABCD',(40,16,14,110)): A.column_dimensions[col].width=w
# ---------- Portfolio
P=wb.create_sheet('Portfolio')
P['A1']='Recommended portfolio: 13 condos'; P['A1'].font=BOLD
cols=['Area','Type','Side','Units','Price per unit ($)','Transfer tax per unit ($)','Setup + closing per unit ($)','All in cost per unit ($)','Total cost ($)',
      'Rev per unit LOW (p25)','Rev per unit CONSERVATIVE (median)','Rev per unit BASE (capped mean)','Rev per unit HIGH (p75)','Fixed costs per unit ($/yr)','Listings in data (n)']
hdr(P,3,cols)
data=[('Downtown Eastside','Condo','East',6,30534,50940,54693,76908,189),
      ('Downtown','Condo','West',5,34563,57838,61550,84710,580),
      ('West End','Condo','West',2,31521,55350,63581,93618,43)]
for i,(nm,ty,sd,u,lo,md,bs,hi,n) in enumerate(data,4):
    P.cell(row=i,column=1,value=nm).font=BLK; P.cell(row=i,column=2,value=ty).font=BLK; P.cell(row=i,column=3,value=sd).font=BLK
    P.cell(row=i,column=4,value=u).font=BLUE
    P.cell(row=i,column=5,value=f"=Assumptions!$B${12 if sd=='East' else 13}").font=GRN
    P.cell(row=i,column=6,value=(f"=Assumptions!$B$16*MIN(E{i},200000)+Assumptions!$B$17*MAX(0,MIN(E{i},2000000)-200000)"
        f"+Assumptions!$B$18*MAX(0,MIN(E{i},3000000)-2000000)+Assumptions!$B$19*MAX(0,E{i}-3000000)")).font=GRN
    P.cell(row=i,column=7,value="=Assumptions!$B$8+Assumptions!$B$9").font=GRN
    P.cell(row=i,column=8,value=f"=E{i}+F{i}+G{i}").font=BLK
    P.cell(row=i,column=9,value=f"=D{i}*H{i}").font=BLK
    for j,v in zip((10,11,12,13),(lo,md,bs,hi)): P.cell(row=i,column=j,value=v).font=BLUE
    P.cell(row=i,column=14,value=f"=E{i}*Assumptions!$B$5+Assumptions!$B$6+Assumptions!$B$7+Assumptions!$B$14").font=GRN
    P.cell(row=i,column=15,value=n).font=BLUE
P['A7']='Total'; P['A7'].font=BOLD
P['D7']='=SUM(D4:D6)'; P['I7']='=SUM(I4:I6)'
for c in ('D7','I7'): P[c].font=BOLD
P['A8']='Unspent reserve ($)'; P['I8']='=Assumptions!B3-I7'
P['A9']='Budget check'; P['I9']='=IF(I7<=Assumptions!B3,"within budget","OVER BUDGET")'
P['A11']='2027 scenarios (use Assumptions B10 and B11 levers)'; P['A11'].font=BOLD
hdr(P,12,['Scenario','','','','Gross revenue ($)','Variable costs ($)','Fixed costs ($)','Extra levy ($)','Net operating income ($)','Net yield on cost'])
for r,(nm,col) in enumerate([('Low (p25)','J'),('Conservative (median)','K'),('Base (capped mean)','L'),('High (p75)','M')],13):
    P.cell(row=r,column=1,value=nm).font=BLK
    P.cell(row=r,column=5,value=f"=SUMPRODUCT($D$4:$D$6,{col}$4:{col}$6)*(1+Assumptions!$B$10)").font=GRN
    P.cell(row=r,column=6,value=f"=E{r}*Assumptions!$B$4").font=GRN
    P.cell(row=r,column=7,value="=SUMPRODUCT($D$4:$D$6,$N$4:$N$6)").font=BLK
    P.cell(row=r,column=8,value="=Assumptions!$B$11*SUMPRODUCT($D$4:$D$6,$E$4:$E$6)").font=GRN
    P.cell(row=r,column=9,value=f"=E{r}-F{r}-G{r}-H{r}").font=BLK
    P.cell(row=r,column=10,value=f"=I{r}/$I$7").font=BLK
P['A18']='Note: portfolio level P10 to P90 range from simulating random listings (base case 4.0%, range 3.0% to 5.2%) is in Alternatives. Spreadsheet scenarios are per listing percentiles applied to every unit, so they are wider than a diversified portfolio would realistically be.'
P['A18'].font=BLK
for r in range(4,10):
    for c in (5,6,7,8,9,10,11,12,13,14): P.cell(row=r,column=c).number_format='$#,##0'
for r in range(13,17):
    for c in (5,6,7,8,9): P.cell(row=r,column=c).number_format='$#,##0'
    P.cell(row=r,column=10).number_format='0.0%'
for i,w in enumerate((22,8,8,8,16,16,16,16,16,16,18,18,16,16,12),1): P.column_dimensions[get_column_letter(i)].width=w
P.row_dimensions[3].height=45
# ---------- data sheets
def put(df,name,note):
    s=wb.create_sheet(name); s['A1']=note; s['A1'].font=BOLD
    hdr(s,3,list(df.columns))
    for r,row in enumerate(df.itertuples(index=False),4):
        for c,v in enumerate(row,1):
            x=s.cell(row=r,column=c,value=(round(v,4) if isinstance(v,float) else v)); x.font=BLUE
    for i in range(1,len(df.columns)+1): s.column_dimensions[get_column_letter(i)].width=20
    return s
alt=pd.read_csv('property_type_comparison.csv').rename(columns={'seg':'type'})
s=put(alt,'Alternatives','Property type comparison (data: Inside Airbnb + REBGV benchmarks; script 06). yld = net yield on all in cost')
n=len(alt)+6
s.cell(row=n,column=1,value='How many properties: yield spread vs number of condos (same $10M area mix, script 06)').font=BOLD
hm=pd.read_csv('how_many_vs_spread.csv')
for c,v in enumerate(hm.columns,1):
    x=s.cell(row=n+1,column=c,value=v); x.font=BOLD; x.fill=HDR
for r,row in enumerate(hm.itertuples(index=False),n+2):
    for c,v in enumerate(row,1): s.cell(row=r,column=c,value=round(float(v),4)).font=BLUE
pc=pd.read_csv('portfolio_compare.csv')[['portfolio','props','deployed','rev_p50','noi_p50','yld_p10','yld_p50','yld_p90']]
m=n+len(hm)+4
s.cell(row=m,column=1,value='Portfolio comparison (script 05): few high value vs many condos').font=BOLD
for c,v in enumerate(pc.columns,1):
    x=s.cell(row=m+1,column=c,value=v); x.font=BOLD; x.fill=HDR
for r,row in enumerate(pc.itertuples(index=False),m+2):
    for c,v in enumerate(row,1): s.cell(row=r,column=c,value=(round(v,4) if isinstance(v,float) else v)).font=BLUE
loc=pd.read_csv('location_evidence.csv'); put(loc,'Location_evidence','Neighbourhood evidence by type (script 07). n = listings in cleaned analysis set; full_lic_share = estimated share of short stay entire homes showing both city and provincial licence numbers')
seas=pd.DataFrame({'month':['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],'review_index':[.53,.60,.74,.86,1.38,1.47,1.72,1.89,1.00,.74,.53,.54]})
put(seas,'Seasonality','Monthly demand index from review dates 2023 to Aug 2026 for the analysis set (1.0 = average month). Use to phase 2027 revenue by month')

S=wb.create_sheet('Sources')
S['A1']='Sources for every number (check each link before presenting)'; S['A1'].font=BOLD
hdr(S,3,['#','Item','Value used','Source','URL','Evidence strength'])
items=[
(1,'REBGV benchmark prices Aug 2026 (East/West condo, house, townhouse)','East condo $628,600; West condo $774,900; East house $1,621,400; West house $2,932,700; East attached $985,400; West attached $1,334,900','Nest Presales Vancouver East and West Market Report, Aug 2026 (repeats REBGV area data). Metro level figures confirmed in GVR stats package','https://www.nestpresales.com/blog/vancouver-real-estate-august-2026-vancouver-east-vancouver-west-market/ ; https://members.gvrealtors.ca/news/GVR-Stats-Package-August-2026.pdf','Good (secondary source for area level; GVR is primary, confirm area numbers in its Vancouver East and West reports)'),
(2,'Metro Vancouver benchmarks Aug 2026 (cross check)','Detached $1,799,400; apartment $686,200; townhouse $1,028,800','Greater Vancouver REALTORS August 2026 stats','https://www.gvrealtors.ca/news/home-sales-continue-downward-trend-to-close-the-summer','Strong (primary)'),
(3,'BC property transfer tax brackets','1% to $200k, 2% to $2M, 3% to $3M, 5% above $3M residential','Government of BC','https://www2.gov.bc.ca/gov/content/taxes/property-taxes/property-transfer-tax','Strong (official)'),
(4,'City of Vancouver Empty Homes Tax','3% of assessed value; exempt only if rented 6+ months in periods of 30+ consecutive days','City of Vancouver','https://vancouver.ca/home-property-development/will-your-home-be-taxed.aspx','Strong (official). Some sites say 5%; the City page says 3%. Check 2027 rate'),
(5,'City of Vancouver STR business licence fee','$1,108 per year plus $77 application','City of Vancouver','https://vancouver.ca/doing-business/short-term-rental-business-licence-requirements.aspx','Strong (official)'),
(6,'Airbnb host fee','3% host only fee (split fee model)','Vancouver STR management blog citing Airbnb fee structure','https://cincinyvrcohost.vercel.app/blog/airbnb-property-management-cost','Medium (vendor blog; confirm on Airbnb help centre)'),
(7,'Management fee','20% (midpoint of 15% to 25%)','AirDNA 2025 report as cited by rentalrealestate.com: 15% to 25%, most near 20% to 25%; Vancouver managers: co-host 15% to 25%, full service 20% to 25%; MasterHost Metro Vancouver 15%','https://rentalrealestate.com/blog/vacation-rental-property-management-fees-explained-costs-percentages-red-flags/ ; https://cincinyvrcohost.vercel.app/blog/cost-of-property-management ; https://masterhost.ca/?p=58182','Medium to good (several independent sources agree)'),
(8,'Utilities, supplies, maintenance','15% of revenue','AirDNA based expense breakdowns (US, 3 bedroom homes): utilities 6% to 17%, supplies 2% to 7%, maintenance 6% to 13%. Whole STR operating costs 30% to 70% of revenue','https://theshorttermshop.com/blue-ridge-short-term-rental-income/ ; https://awning.com/post/airbnb-profit-margin-benchmarks-2026-what-good-really-looks-like-by-market-type','Medium (US data, larger homes). Not Vancouver specific'),
(9,'Vancouver 2026 residential property tax rate','0.336394% of assessed value ($3.36394 per $1,000)','City of Vancouver council 2026 rate documents (school 0.98001, TransLink 0.35860, BC Assessment 0.03814, MFA 0.00020 per $1,000) and a published rate table','https://council.vancouver.ca/20260505/documents/a3.pdf ; https://catax.tools/property-tax-vancouver/','Good'),
(10,'Strata fees','$0.525 per sq ft per month x 600 sq ft = $3,780 per year','Vancouver $0.35 to $0.70 per sq ft (WelcomeAide); Metro Vancouver about $0.45 (Straw Homes); downtown amenity buildings above $0.80','https://welcomeaide.com/en/blog/condo-fees-maintenance-costs-explained-newcomers-canada-2026 ; https://www.strawhomes.com/what-is-included-in-a-condo-maintenance-fee/','Medium. 600 sq ft unit size is an assumption (typical one bedroom)'),
(11,'Typical Vancouver STR revenue cross check','Vancouver 1BR average about C$58,000 per year','Cin Cin YVR Co-Host (vendor blog). Our median condo revenue is $49,556, so ours is more conservative','https://cincinyvrcohost.vercel.app/blog/airbnb-property-management-cost','Weak (vendor), used only as a sanity check'),
(12,'STR insurance','$2,000 per year per condo','US STR policy examples $2,200 to $3,200 (3 to 5 bedroom); owner condo policy $300 to $900','https://theshorttermshop.com/southern-utah-short-term-rental-income/ ; https://welcomeaide.com/en/blog/condo-fees-maintenance-costs-explained-newcomers-canada-2026','Weak. Get a broker quote'),
(13,'Furnishing and setup','$10,000 condo, $15,000 townhouse, $20,000 house','Airbtics Canada: 1BR $4,829, 2BR $6,795, 3BR $8,576; corporatestays 2026 CAD 1BR quality furniture $6,000 to $10,000 plus kitchenware and linens $1,500 to $2,500; Awning $10,000 to $30,000','https://airbtics.com/starting-an-airbnb-canada/ ; https://stage2.corporatestays.com/?p=313349 ; https://awning.com/post/how-to-furnish-an-airbnb','Medium'),
(14,'Other closing costs','$4,000 per purchase','BC worked example $900k: legal $1,500, title insurance $250, tax adjustment $1,500, inspection $600 = $3,850','https://canadianmoneyhelp.ca/?p=842','Medium'),
(15,'Revenue','Inside Airbnb estimated_revenue_l365d','Inside Airbnb Vancouver files provided in the case (snapshot file dated 2026-09-17)','https://insideairbnb.com/get-the-data/','Data (estimate by Inside Airbnb, not reported bookings)')]
for r,row in enumerate(items,4):
    for c,v in enumerate(row,1):
        x=S.cell(row=r,column=c,value=v); x.font=BLK; x.alignment=Alignment(wrap_text=True,vertical='top')
for col,w in zip('ABCDEF',(5,38,45,70,70,40)): S.column_dimensions[col].width=w

wb.save('DDD_handoff_workbook.xlsx')
