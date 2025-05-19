import pandas as pd
import json
import pycountry

# Load the CSV data
df = pd.read_csv("oxford-government-response.csv")

# Calculate total measures (sum of columns for each country/date)
df['total_measures'] = df.iloc[:, 2:-1].sum(axis=1)

# Get ISO Alpha-3 code
df['iso_a3'] = df['location_key'].astype(str).apply(lambda x: x.split('_')[0] if '_' in x else x)

# Convert ISO Alpha-2 to Alpha-3
def alpha2_to_alpha3(alpha2_code):
    try:
        return pycountry.countries.get(alpha_2=alpha2_code).alpha_3
    except AttributeError:
        return None

df['iso_a3'] = df['iso_a3'].apply(alpha2_to_alpha3)
df = df.dropna(subset=['iso_a3'])

# Aggregate data by country + date
df_country = df.groupby(['iso_a3', 'date'], as_index=False)['total_measures'].sum()

# Normalize the measures (if there are non-zero values)
df_country['normalized_measures'] = df_country['total_measures'] / df_country['total_measures'].quantile(0.95)
df_country['normalized_measures'] = df_country['normalized_measures'].clip(upper=1)

# Save data to JSON
df_country.to_json("data/government_measures.json", orient="records")
