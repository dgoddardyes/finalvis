import pandas as pd
import pycountry
from pycountry_convert import country_alpha2_to_continent_code

# Load your CSV file
df = pd.read_csv("vaccination_gdp_final5.csv")

# Function to get continent based on country name
def get_continent(country_name):
    try:
        # Attempt to find the country based on the name
        country = pycountry.countries.get(name=country_name)
        if not country:
            return 'Unknown'  # If the country name is not found

        # Attempt to convert the alpha-2 code to continent code
        continent_code = country_alpha2_to_continent_code(country.alpha_2)
        
        # Mapping continent codes to continent names
        continent_map = {
            'AF': 'Africa',
            'AN': 'Antarctica',
            'AS': 'Asia',
            'EU': 'Europe',
            'NA': 'North America',
            'OC': 'Oceania',
            'SA': 'South America'
        }

        return continent_map.get(continent_code, 'Unknown')

    except (AttributeError, KeyError):
        # Catch errors related to invalid country code or other issues
        return 'Unknown'

# Add a new column for the continent
df['continent'] = df['country_name'].apply(get_continent)

# Save the updated CSV to a new file
df.to_csv("vaccination_continent.csv", index=False)
