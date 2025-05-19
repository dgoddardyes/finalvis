import pandas as pd
import pycountry

# Define the lookup function for country name based on location_key
def lookup_country(code):
    try:
        country = pycountry.countries.get(alpha_2=code)
        return country.name if country else None
    except:
        return None

# Load the datasets
demographics = pd.read_csv('demographics_stats_countries.csv')
vaccinations = pd.read_csv('vaccine_stats_countries.csv')
economy = pd.read_csv('economy.csv')  # GDP data

# Merge vaccinations with demographics
combined = vaccinations.merge(
    demographics[['location_key', 'population']],
    on='location_key',
    how='left'
)

# Drop unneeded vaccine-specific columns
columns_to_drop = [
    'new_persons_vaccinated_pfizer', 'cumulative_persons_vaccinated_pfizer',
    'new_persons_fully_vaccinated_pfizer', 'cumulative_persons_fully_vaccinated_pfizer',
    'new_vaccine_doses_administered_pfizer', 'cumulative_vaccine_doses_administered_pfizer',
    'new_persons_vaccinated_moderna', 'cumulative_persons_vaccinated_moderna',
    'new_persons_fully_vaccinated_moderna', 'cumulative_persons_fully_vaccinated_moderna',
    'new_vaccine_doses_administered_moderna', 'cumulative_vaccine_doses_administered_moderna',
    'new_persons_vaccinated_janssen', 'cumulative_persons_vaccinated_janssen',
    'new_persons_fully_vaccinated_janssen', 'cumulative_persons_fully_vaccinated_janssen',
    'new_vaccine_doses_administered_janssen', 'cumulative_vaccine_doses_administered_janssen',
    'new_persons_vaccinated_sinovac', 'total_persons_vaccinated_sinovac',
    'new_persons_fully_vaccinated_sinovac', 'total_persons_fully_vaccinated_sinovac',
    'new_vaccine_doses_administered_sinovac', 'total_vaccine_doses_administered_sinovac'
]
combined.drop(columns=columns_to_drop, inplace=True, errors='ignore')

# Convert 'date' to datetime
combined['date'] = pd.to_datetime(combined['date'], errors='coerce')

# Filter for relevant date range
combined = combined[combined['date'] >= pd.Timestamp('2020-12-13')]

# Create full date range
all_dates = pd.date_range(start='2020-12-13', end=combined['date'].max(), freq='D')
complete_dates = pd.DataFrame({'date': all_dates})

# Fill missing dates for each country
countries = combined['location_key'].unique()
combined_full = pd.DataFrame()

for country in countries:
    country_data = combined[combined['location_key'] == country]
    country_dates = complete_dates.copy()
    country_dates['location_key'] = country
    country_data = pd.merge(
        country_dates,
        country_data[['location_key', 'date', 'cumulative_persons_fully_vaccinated', 'population']],
        on=['location_key', 'date'],
        how='left'
    )
    
    # Fill missing vaccination and population data
    country_data['cumulative_persons_fully_vaccinated'] = country_data['cumulative_persons_fully_vaccinated'].ffill().bfill()
    country_data['population'] = country_data['population'].ffill().bfill()
    
    # Calculate % vaccinated
    country_data['percent_vaccinated'] = (
        country_data['cumulative_persons_fully_vaccinated'] / country_data['population']
    ) * 100
    country_data.loc[country_data['cumulative_persons_fully_vaccinated'] == 0, 'percent_vaccinated'] = 0.0
    country_data['percent_vaccinated'] = country_data['percent_vaccinated'].clip(upper=100).round(2)

    # Add formatted date string for animation
    country_data['date_str'] = country_data['date'].dt.strftime('%Y-%m-%d')
    
    combined_full = pd.concat([combined_full, country_data])

# Reset index and finalize
combined_full.reset_index(drop=True, inplace=True)

# Add country name
combined_full['country_name'] = combined_full['location_key'].apply(lookup_country)

# Merge GDP data
economy['location_key'] = economy['location_key'].astype(str).str.upper()
combined_full['location_key'] = combined_full['location_key'].astype(str).str.upper()
combined_full = combined_full.merge(
    economy[['location_key', 'gdp_usd', 'gdp_per_capita_usd']],
    on='location_key',
    how='left'
)

# Optional: Warn about missing GDP data
missing_gdp = combined_full[combined_full['gdp_usd'].isna()]['location_key'].unique()
if len(missing_gdp) > 0:
    print("Countries missing GDP data:")
    print(missing_gdp)
else:
    print("GDP data successfully merged for all countries.")

# Save the final clean CSV
combined_full.to_csv('vaccination_gdp_final.csv', index=False)