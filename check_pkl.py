import pandas as pd
data = pd.read_pickle('loss curves/gpt_loss+lrs.pkl')
print("Type of loaded data:", type(data))
if isinstance(data, dict):
    print("\nKeys in dictionary:")
    print(list(data.keys()))
    
    # Check structure of first DataFrame
    first_key = list(data.keys())[0]
    df = data[first_key]
    print(f"\n\nChecking '{first_key}':")
    print(f"Type: {type(df)}")
    print(f"Shape: {df.shape}")
    print(f"\nColumn names:")
    print(df.columns.tolist())
    print(f"\nFirst few rows:")
    print(df.head())
    print(f"\nData types:")
    print(df.dtypes)
else:
    print("\nData structure:")
    print(data)
