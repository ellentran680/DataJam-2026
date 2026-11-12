"""Adds Part 3 and Part 4 sheets (from results CSVs) to the handoff workbook. Usage: python add_part3_part4_sheets.py results workbook.xlsx"""
import sys, pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
res, wbp = sys.argv[1], sys.argv[2]
wb = load_workbook(wbp)
HDR = PatternFill('solid', fgColor='D9E1F2'); F = lambda **k: Font(name='Arial', size=10, **k)
sheets = [('P3_base_case_PnL', 'part3_base_case_pnl.csv', 'Part 3: base case 2027 profit and loss, 13 condos (script ddd_part3_part4.py)'),
          ('P3_cases', 'part3_cases.csv', 'Part 3: low, conservative, base, high cases and spread over the 2.5% Bank of Canada policy rate'),
          ('P3_monthly_2027', 'part3_monthly_2027.csv', 'Part 3: base case by month (revenue phased with the review seasonality index)'),
          ('P3_sensitivity', 'part3_sensitivity.csv', 'Part 3: one driver at a time, yield bad and good case'),
          ('P3_breakeven', 'part3_breakeven.csv', 'Part 3: break even revenue and booked nights'),
          ('P3_total_return', 'part3_total_return.csv', 'Part 3: income plus price change (value moves with purchase price)'),
          ('P4_demand_check', 'part4_demand_check.csv', 'Part 4: reviews 2026 versus 2025 for established listings (World Cup check)'),
          ('P4_risk_register', 'part4_risk_register.csv', 'Part 4: ranked risks with size and mitigation')]
for name, f, note in sheets:
    if name in wb.sheetnames: del wb[name]
    df = pd.read_csv(f'{res}/{f}'); ws = wb.create_sheet(name); ws['A1'] = note; ws['A1'].font = F(bold=True)
    for c, h in enumerate(df.columns, 1):
        x = ws.cell(row=3, column=c, value=h); x.font = F(bold=True); x.fill = HDR; x.alignment = Alignment(wrap_text=True, vertical='top')
    for r, row in enumerate(df.itertuples(index=False), 4):
        for c, v in enumerate(row, 1):
            if pd.isna(v): v = None
            elif isinstance(v, float): v = round(v, 4)
            ws.cell(row=r, column=c, value=v).font = F(color='0000FF')
    for c in range(1, len(df.columns) + 1): ws.column_dimensions[get_column_letter(c)].width = 24
wb.save(wbp)
