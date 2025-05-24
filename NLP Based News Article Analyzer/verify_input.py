import pandas as pd
df = pd.read_excel('input.xlsx')
print("First 5 rows:")
print(df.head())
print("\nColumns:", list(df.columns))
print("\nNumber of URLs:", len(df))