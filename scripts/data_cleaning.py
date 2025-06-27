import pandas as pd
import re

def clean_startup_data(path):
    df = pd.read_csv(path)

    # Drop completely empty rows
    df.dropna(how='all', inplace=True)

    # Lowercase and clean column headers
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Rename known columns to a standard format
    df.rename(columns={
        "startup_name": "Startup Name",
        "industry": "Industry Vertical",
        "industry_vertical": "Industry Vertical",
        "investment_amount_(usd)": "Total Funding (USD)",
        "total_funding_(usd)": "Total Funding (USD)",
        "year_founded": "Year",
        "country": "Country",
        "city": "City"
    }, inplace=True)

    # Remove duplicates
    df.drop_duplicates(inplace=True)

    # Clean funding values
    def convert_funding(val):
        try:
            if pd.isna(val):
                return None
            val = str(val).lower().replace(",", "").replace("$", "").strip()

            # Normalize values like "10 million", "5.5m", "2b"
            val = re.sub(r"(\d+\.?\d*)\s*m(?:illion)?", r"\1e6", val)
            val = re.sub(r"(\d+\.?\d*)\s*b(?:illion)?", r"\1e9", val)
            val = val.replace("mn", "e6").replace("bn", "e9")

            return float(eval(val))
        except:
            return None

    df["Total Funding (USD)"] = df["Total Funding (USD)"].apply(convert_funding)

    # Convert year column to numeric
    df["Year"] = pd.to_numeric(df["Year"], errors='coerce').astype("Int64")

    # Drop rows missing critical info
    df.dropna(subset=["Startup Name", "Industry Vertical", "Total Funding (USD)", "Year"], inplace=True)

    # Standardize text columns
    df["Industry Vertical"] = df["Industry Vertical"].str.title().str.strip()

    if "Country" in df.columns:
        df["Country"] = df["Country"].str.title().str.strip()

    if "City" in df.columns:
        df["City"] = df["City"].str.title().str.strip()

    # Optional: Add Month if needed in future
    if "Month" not in df.columns:
        df["Month"] = None

    return df
