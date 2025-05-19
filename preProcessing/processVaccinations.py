import pandas as pd


demographics = pd.read_csv('demographics_stats_countries.csv')
vaccinations = pd.read_csv('vaccine_stats_countries.csv')

# merge the datasets on 'location_key'
combined = vaccinations.merge(
    demographics[['location_key', 'population']],
    on='location_key',
    how='left'  # 'left' to keep all vaccination records
)

# columns_to_drop
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

# drop the columns_to_drop columns
combined.drop(columns=columns_to_drop, inplace=True, errors='ignore')

# add a new column for percent vaccinated and then round to 2 decimal places
combined['percent_vaccinated'] = (combined['cumulative_persons_fully_vaccinated'] / combined['population']) * 100
combined['percent_vaccinated'] = combined['percent_vaccinated'].round(2)


# Convert to datetime format
combined['date'] = pd.to_datetime(combined['date'], errors='coerce')

combined.reset_index(drop=True, inplace=True)

combined.to_csv('vaccinations_with_population_indexed.csv', index=False)
