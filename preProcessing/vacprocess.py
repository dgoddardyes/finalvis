import pandas as pd
import pycountry

df = pd.read_csv("data/vaccinations.csv", dtype=str)


# remove any entries from location_key that contain an underscore or number
df_clean = df[df["location_key"].notna() & df["location_key"].str.match(r"^[A-Za-z]+$")]

# reset index afterwards
df_clean = df_clean.reset_index(drop=True)

# match country code to pycountry
def lookup_country(code):
    try:
        country = pycountry.countries.get(alpha_2=code)
        return country.name if country else None
    except:
        return None

# apply name to country_name column based off pycountry lookup
df_clean["country_name"] = df_clean["location_key"].apply(lookup_country)

df_clean.to_csv("vaccine_stats_countries.csv", index=False)