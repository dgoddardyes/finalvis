import pandas as pd
import pycountry

df = pd.read_csv("data/health.csv", dtype=str)

# remove states and provinces, so only full countries
df_clean = df[df["location_key"].notna() & df["location_key"].str.match(r"^[A-Za-z]+$")]

# dropping hospital_beds_per_1000 cause theres barely any data for it anyway
df_clean = df_clean.drop(columns=["hospital_beds_per_1000"])


df_clean = df_clean.reset_index(drop=True)

# replace NaN values with 77777
df_clean = df_clean.fillna(77777)

# add country names based on the location_key (ISO 3166-1 alpha-2 codes)
def lookup_country(code):
    try:
        country = pycountry.countries.get(alpha_2=code)
        return country.name if country else None
    except:
        return None

df_clean["country_name"] = df_clean["location_key"].apply(lookup_country)


df_clean.to_csv("health_stats_countries_final_actual.csv", index=False)

