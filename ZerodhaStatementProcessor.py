import pandas as pd
from ExtractHeader import extract_section_dataframe

pd.options.display.float_format = '{:.2f}'.format

HOLDING_ST = 'HP≤365'
HOLDING_LT = 'HP>365'
HOLDING_INTRADAY = 'HP=0'
HOLDING_NON_EQUITY = 'Non-Equity'
# HOLDING_DEBT = 'Debt'

COL_HOLDING_PERIOD_GROUP = 'HoldPeriodGroup'

COL_ENTRY_DATE = "Entry Date"
COL_EXIT_DATE = "Exit Date"
COL_BUY_VALUE = "Buy Value"
COL_SELL_VALUE = "Sell Value"
COL_PROFIT_BEFORE_EXPENSE = "Profit"
COL_NET_PROFIT = "Net Profit"

COL_PERIOD_OF_HOLDING = "Period of Holding"
COL_EXIT_BUCKET = "Exit Bucket"
COL_EXPENSE = "Expense"

header_columns = [COL_ENTRY_DATE, COL_EXIT_DATE, COL_BUY_VALUE, COL_SELL_VALUE, COL_PROFIT_BEFORE_EXPENSE
                  #, "Period of Holding"
                  ]
columns_expenses = ['Brokerage', 'Exchange Transaction Charges', 'IPFT', 
                    'SEBI Charges', 
                    'CGST', 'SGST',	'IGST',	'Stamp Duty']



# --- map Section/Category to HoldPeriodGrou ---
def classify_hp(row):
    sec = str(row.get("Section", "")).strip().lower()
    hp = row.get("Period of Holding")    
    
    if pd.isna(hp): 
        return "Unknown"
    if hp == 0: 
        return "HP=0"
    elif 0 < hp <= 365: 
        return HOLDING_ST
    elif hp > 365: 
        return HOLDING_LT
    
    # Non Equity → ignore
  #  if "non equity" in sec:
   #     return "Ignore"
    
    return "Unknown"

BUCKET_B1 = "B1: 1-Apr to 15-Jun"
BUCKET_B2 = "B2: 16-Jun to 15-Sep"
BUCKET_B3 = "B3: 16-Sep to 15-Dec"
BUCKET_B4 = "B4: 16-Dec to 15-Mar"
BUCKET_B5 = "B5: 16-Mar to 31-Mar"
bucket_order = [BUCKET_B1, BUCKET_B2, BUCKET_B3, BUCKET_B4, BUCKET_B5]

# --- Exit Date bucket function ---
def exit_bucket(d: pd.Timestamp) -> str:
    if pd.isna(d): return "Unknown"
    fy = d.year if d.month >= 4 else d.year - 1
    
    ranges = [
        (BUCKET_B1, pd.Timestamp(fy, 4, 1),  pd.Timestamp(fy, 6, 15)),
        (BUCKET_B2, pd.Timestamp(fy, 6, 16), pd.Timestamp(fy, 9, 15)),
        (BUCKET_B3, pd.Timestamp(fy, 9, 16), pd.Timestamp(fy, 12, 15)),
        (BUCKET_B4, pd.Timestamp(fy, 12, 16), pd.Timestamp(fy+1, 3, 15)),
        (BUCKET_B5, pd.Timestamp(fy+1, 3, 16), pd.Timestamp(fy+1, 3, 31)),
    ]
     
    '''
    ranges = [
        (BUCKET_B1, pd.Timestamp(fy, 4, 1),  pd.Timestamp(fy, 7, 22)),
        (BUCKET_B2, pd.Timestamp(fy, 7, 23), pd.Timestamp(fy + 1, 3, 31)),
#        (BUCKET_B3, pd.Timestamp(fy, 9, 16), pd.Timestamp(fy, 12, 15)),
#        (BUCKET_B4, pd.Timestamp(fy, 12, 16), pd.Timestamp(fy+1, 3, 15)),
#        (BUCKET_B5, pd.Timestamp(fy+1, 3, 16), pd.Timestamp(fy+1, 3, 31)),
    ]
    '''     

    '''
    ranges = [
    (BUCKET_B1, pd.Timestamp(fy, 4, 1),  pd.Timestamp(fy, 6, 15)),
    (BUCKET_B2, pd.Timestamp(fy, 6, 16), pd.Timestamp(fy, 7, 22)),
    (BUCKET_B3, pd.Timestamp(fy, 7, 23),  pd.Timestamp(fy, 9, 15)),
#        (BUCKET_B3, pd.Timestamp(fy, 9, 16), pd.Timestamp(fy, 12, 15)),
#        (BUCKET_B4, pd.Timestamp(fy, 12, 16), pd.Timestamp(fy+1, 3, 15)),
#        (BUCKET_B5, pd.Timestamp(fy+1, 3, 16), pd.Timestamp(fy+1, 3, 31)),
    ]
    '''
    
    for name, start, end in ranges:
        if start <= d <= end:
            return name
    return "Out of FY"

"""
def assign_exit_bucket(df : pd.DataFrame):
    df["Exit Date"] = pd.to_datetime(df["Exit Date"], errors="coerce")
    df["Exit Bucket"] = df["Exit Date"].apply(exit_bucket)
    
    return
"""

def assign_exit_bucket(df : pd.DataFrame, date_col: str = "Exit Date", bucket_col: str = "Exit Bucket"):
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df[bucket_col] = df[date_col].apply(exit_bucket)
    
    return


def consolidate_expenses(df: pd.DataFrame):    
    # Keep only the columns that exist in df
    valid_cols = [col for col in columns_expenses if col in df.columns]

    # Work on a copy to avoid modifying the original
    

    # Add new column with row-wise sum
    df[COL_EXPENSE] = df[valid_cols].sum(axis=1)

    # Drop the original expense columns
    df.drop(columns=valid_cols, inplace=True)   

    return

def calculate_net_profit(df: pd.DataFrame):
    if COL_NET_PROFIT not in df.columns:
        df[COL_NET_PROFIT] = df[COL_PROFIT_BEFORE_EXPENSE] - df[COL_EXPENSE]
    return

    # Qty	Sale Date	Sale Rate	Sale Value	Purchase Date	Purchase Rate	Purchase Value	Profit/Loss(-)
def ProcessIciciDirect(df: pd.DataFrame) -> pd.DataFrame:

    # Qty	Sale Date	Sale Rate	Sale Value	Purchase Date	Purchase Rate	Purchase Value	Profit/Loss(-)

    COL_QTY = 'Qty'
    COL_SALE_DATE = 'Sale Date'
    COL_SALE_RATE = 'Sale Rate'
    COL_SALE_VALUE = 'Sale Value'
    COL_PURCHASE_DATE = 'Purchase Date'
    COL_PURCHASE_RATE = 'Purchase Rate'
    COL_PURCHASE_VALUE = 'Purchase Value'
    COL_PROFIT_BEFORE_EXPENSE = 'Profit/Loss(-)'

    df[COL_SALE_DATE] = pd.to_datetime(df[COL_SALE_DATE], errors='coerce')
    df[COL_PURCHASE_DATE] = pd.to_datetime(df[COL_PURCHASE_DATE], errors='coerce')

    def calculate_expense(row):
        qty = row.get(COL_QTY)
        net_sale_value = row.get(COL_SALE_VALUE)
        purchase_value = row.get(COL_PURCHASE_VALUE)
        sale_rate = row.get(COL_SALE_RATE)
        purchase_rate = row.get(COL_PURCHASE_RATE)

        sale_expense = qty * sale_rate - net_sale_value
        purchase_expense = purchase_value - qty * purchase_rate

        return sale_expense + purchase_expense       

    df[COL_EXPENSE] = df["Sale Expenses"] + df["Purchase Expenses"]
#df.apply(calculate_expense, axis=1)
    df[COL_PURCHASE_VALUE] = df[COL_QTY] * df[COL_PURCHASE_RATE]
    df[COL_SALE_VALUE] = df[COL_QTY] * df[COL_SALE_RATE]
    df[COL_PROFIT_BEFORE_EXPENSE] = df[COL_SALE_VALUE] - df[COL_PURCHASE_VALUE]

    df = df.rename(columns={
        COL_PURCHASE_DATE: COL_ENTRY_DATE,
        COL_SALE_DATE: COL_EXIT_DATE,
        COL_PURCHASE_VALUE: COL_BUY_VALUE,
        COL_SALE_VALUE: COL_SELL_VALUE,
        COL_PROFIT_BEFORE_EXPENSE: 'Profit'})
    
    df = df[header_columns +  [COL_EXPENSE]]
    
    return df
# --- paths ---
input_file = r"E:\Dropbox\ITR calculation\FY 202526\Anuj\taxpnl_zerodha.xlsx"
iciciDirect_file = r"E:\Dropbox\ITR calculation\FY 202526\Anuj\icici.xlsx"
dividend_file = r"E:\Dropbox\ITR calculation\FY 202526\Anuj\Calc.xlsx"
dividend_sheet = "Dividends"

sheet = "Tradewise Exits from 2025-04-01"

df_dividends = pd.read_excel(dividend_file, sheet_name=dividend_sheet)
df_dividends["Date"] = pd.to_datetime(df_dividends["Date"], dayfirst=True)


assign_exit_bucket(df_dividends, date_col="Date", bucket_col="Date Bucket")

df_dividends = df_dividends.groupby("Date Bucket")["Dividend"].sum().reset_index()
print (df_dividends)

df_NonEquity = extract_section_dataframe (input_file, sheet, header_columns, section="Non Equity")
assign_exit_bucket(df_NonEquity)
#consolidate_expenses(df_NonEquity)
df_NonEquity[COL_EXPENSE] = 0
calculate_net_profit(df_NonEquity)
df_NonEquity[COL_HOLDING_PERIOD_GROUP] = HOLDING_NON_EQUITY
# print ('------- Non-Equity summary -------')
# print(df_NonEquity)


df_Intraday = extract_section_dataframe (input_file, sheet, header_columns + columns_expenses, section="Equity - Intraday")
assign_exit_bucket(df_Intraday)
consolidate_expenses(df_Intraday)

# print(df_Intraday)
df_Intraday[COL_HOLDING_PERIOD_GROUP] = HOLDING_INTRADAY
calculate_net_profit(df_Intraday)

print(df_Intraday)

df_Eq_ST_Zerodha = extract_section_dataframe (input_file, sheet, header_columns + columns_expenses, section="Equity - Short Term")
#consolidate_expenses(df_Eq_ST_Zerodha)
df_Eq_ST_Zerodha[COL_EXPENSE] = 0

print(df_Eq_ST_Zerodha)

df_Eq_ST_icici = pd.read_excel(iciciDirect_file, sheet_name='ShortTerm')
# print(df_Eq_ST_icici)
df_Eq_ST_icici = ProcessIciciDirect(df_Eq_ST_icici)
#df_Eq_ST_icici = assign_exit_bucket(df_Eq_ST_icici)ch
# print(df_Eq_ST_icici)

df_Eq_LT_icici = pd.read_excel(iciciDirect_file, sheet_name='LongTerm')
df_Eq_LT_icici = ProcessIciciDirect(df_Eq_LT_icici)

# print(df_Eq_LT_icici)


#df_Eq_ST_icici = None
df_Eq_ST = pd.concat([df_Eq_ST_Zerodha, df_Eq_ST_icici], ignore_index=True)

df_Eq_ST[COL_HOLDING_PERIOD_GROUP] = HOLDING_ST
assign_exit_bucket(df_Eq_ST)
# consolidate_expenses(df_Eq_ST)
calculate_net_profit(df_Eq_ST)
# print(df_Eq_ST)

df_Eq_LT_Zerodha = extract_section_dataframe (input_file, sheet, header_columns + columns_expenses, section="Equity - Long Term")
#consolidate_expenses(df_Eq_LT_Zerodha)
df_Eq_LT_Zerodha[COL_EXPENSE] = 0

#df_Eq_LT_icici = None
df_Eq_LT = pd.concat([df_Eq_LT_Zerodha, df_Eq_LT_icici], ignore_index=True)

df_Eq_LT[COL_HOLDING_PERIOD_GROUP] = HOLDING_LT
assign_exit_bucket(df_Eq_LT)
#consolidate_expenses(df_Eq_LT)
calculate_net_profit(df_Eq_LT)
# print(df_Eq_LT)

df_MutualFunds = extract_section_dataframe (input_file, "Mutual Funds", ["Symbol"], section="Debt - Purchases post 2023-04-01")
debt_MFs = df_MutualFunds["Symbol"].unique().tolist();



df_MF_All = extract_section_dataframe (input_file, sheet, header_columns + [COL_PERIOD_OF_HOLDING, "Symbol"], section="Mutual Funds")
assign_exit_bucket(df_MF_All)
df_MF_All[COL_EXPENSE] = 0.0
calculate_net_profit(df_MF_All)

df_MF_Equity = df_MF_All[~df_MF_All["Symbol"].isin(debt_MFs)].copy()
df_MF_Equity = df_MF_Equity.drop(columns='Symbol')
df_MF_Equity[COL_HOLDING_PERIOD_GROUP] = df_MF_Equity.apply(classify_hp, axis=1)

# print (df_MF_Equity);

df_MF_Debt = df_MF_All[df_MF_All["Symbol"].isin(debt_MFs)].copy()
df_MF_Debt = df_MF_Debt.drop(columns='Symbol')
df_MF_Debt[COL_HOLDING_PERIOD_GROUP] = HOLDING_NON_EQUITY ## because we treat debt MF same as non-equity for tax purposes

# print(df_MF_Debt)

del df_MF_All

# print(df_MF_All)

output_file = "taxpnl_summary_new.xlsx"

interestingCols = [COL_HOLDING_PERIOD_GROUP, COL_EXIT_BUCKET, COL_BUY_VALUE, COL_SELL_VALUE, COL_PROFIT_BEFORE_EXPENSE, COL_EXPENSE, COL_NET_PROFIT]
df_Eq_ST = df_Eq_ST[interestingCols]
df_Eq_LT = df_Eq_LT[interestingCols]
df_MF_Equity = df_MF_Equity[interestingCols]
df_MF_Debt = df_MF_Debt[interestingCols]
df_Intraday = df_Intraday[interestingCols]
df_NonEquity = df_NonEquity[interestingCols]


# print(df_MutualFunds)

df_Eq_ST = None
df_Eq_LT = None
#df_MF_Equity = None
# df_MF_Debt = None
df_Intraday = None
df_NonEquity = None


df = pd.concat([df_Eq_ST, df_Eq_LT, df_MF_Equity, df_MF_Debt, df_Intraday, df_NonEquity], ignore_index=True)[interestingCols]
#print(len(df))
# --- filter valid ---
df = df[(df[COL_HOLDING_PERIOD_GROUP].isin([HOLDING_INTRADAY, 
                                            # HOLDING_DEBT,
                                              HOLDING_ST, HOLDING_LT, HOLDING_NON_EQUITY])) & (df[COL_EXIT_BUCKET] != "Unknown")]

#print(df)

# print(df.to_string(max_cols=None))

def aggregate(df: pd.DataFrame, col: str) -> pd.DataFrame:
    
    # --- aggregate ---

    # Group by HoldPeriodGroup and Exit Bucket, summing Profit
    grouped = df.groupby([COL_HOLDING_PERIOD_GROUP, COL_EXIT_BUCKET])[col].sum().reset_index()

    # Pivot to get Profit for each Exit Bucket as columns
    pivot = grouped.pivot(index=COL_HOLDING_PERIOD_GROUP, columns=COL_EXIT_BUCKET, values=col)

    # Reindex to include all buckets and holding periods, filling missing values with 0
    pivot = pivot.reindex(columns=bucket_order, index=[HOLDING_INTRADAY, HOLDING_ST, HOLDING_LT, HOLDING_NON_EQUITY]).fillna(0)

    # Add Total column summing profits across buckets
    pivot['Total'] = pivot[bucket_order].sum(axis=1)

    # Reset index to make HoldPeriodGroup a column
    pivot = pivot.reset_index()
    return pivot

pivot_sell_value = aggregate(df, COL_SELL_VALUE)
print ('------- Sell Value summary -------')
print(pivot_sell_value)

pivot_buy_value = aggregate(df, COL_BUY_VALUE)
print ('------- Buy Value summary -------')
print(pivot_buy_value)


pivot_profit_before_expense = aggregate(df, COL_PROFIT_BEFORE_EXPENSE)
print ('------- Profit (before expenses) summary -------')
print(pivot_profit_before_expense)

pivot_expense = aggregate(df, COL_EXPENSE)
print ('------- Expenses summary -------')
print(pivot_expense)


print ('------- Net Profit summary -------')
pivot_net_profit = aggregate(df, COL_NET_PROFIT)
print(pivot_net_profit)

# --- save ---
# pivot.to_excel(output_file, sheet_name="Summary_3x5", index=False)

# print("✅ Done. Wrote:", output_file)

