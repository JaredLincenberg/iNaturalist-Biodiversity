# Depends on globals from main.py 
# Pandas and NP are needed.

def get_species_density():
    countyDetails = get_county_properties().json()
    df = get_county_dataframe()
    for feature in countyDetails['features']:
        name = feature['properties']['NAME']
        area = feature['properties']['Shape__Area']
        sqmi = feature['properties']['SQMI']
        population = feature['properties']['POPULATION']
        df.loc[df['county_name'] == name, 'population'] = population
        df.loc[df['county_name'] == name, 'area'] = area
        df.loc[df['county_name'] == name, 'sqmi'] = sqmi
    df['species_density'] = df.apply(lambda row: int(row['species_count'])/float(row['area']), axis=1, result_type='expand')
    df['species_density_per_sq_mi'] = df.apply(lambda row: int(row['species_count'])/float(row['sqmi']), axis=1, result_type='expand')
    df['species_density_log'] = df.apply(lambda row: 0 if row['species_density'] == 0 else np.log(row['species_density']), axis=1, result_type='expand')
    df['species_per_person'] = df.apply(lambda row: int(row['species_count'])/float(row['population']), axis=1, result_type='expand')
    df['species_per_person_log'] = df.apply(lambda row: 0 if row['species_per_person'] == 0 else np.log(row['species_per_person']), axis=1, result_type='expand')
    df['species_per_person_demoniator_log'] = df.apply(lambda row: 0 if row['species_per_person'] == 0 else int(row['species_count'])/np.log(float(row['population'])), axis=1, result_type='expand')
    return df 
