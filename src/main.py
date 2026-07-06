from datetime import datetime
from functools import cache
import os
from pickle import GLOBAL
from time import sleep

import requests
import csv
import plotly.express as px
from urllib.request import urlopen
import json
import pandas as pd
import requests_cache      
import numpy as np
# requests_cache.install_cache('cache/inaturalist_cache', backend='sqlite', expire_after=1800)

INAT_COLORADO_ID = 34
INAT_USA_ID = 1
INAT_NORTH_AMERICA_ID = 97394
INAT_PLACE_TYPE_COUNTY = 9
INAT_ADMIN_LEVEL_COUNTY = 20

COUNTY_GEOJSON = None
COUNTY_PROPERTIES = None
INAT_COUNTY_DATAFRAME = None
INAT_COUNTY_DATA = None
TAXONOMY_DATA = None
COUNTY_SPECIES = None

#### Get the counties for a given state ID from the iNaturalist places CSV file
def get_USA_State_Counties(id):
    counties = []
    with open('data/raw/inaturalist-places.csv', 'r') as files:
        reader = csv.DictReader(files)
        for row in reader:
            if row['ancestry'] == str(INAT_NORTH_AMERICA_ID) + "/" + str(INAT_USA_ID) + "/" + str(id) and row['place_type'] == str(INAT_PLACE_TYPE_COUNTY) and row['admin_level'] == str(INAT_ADMIN_LEVEL_COUNTY):
                counties.append(row)
    return counties

### Call the iNaturalist API to get the species counts for a given county ID
def get_County_Species_Counts(county_id, rank='species', acc_below="1000", page=1, per_page=500, native=None, invasive=None,endemic=None,threatened=None, captive="false", identified="true", photos="true", verifiable="true", quality_grade="research"):

    params = {
        "verifiable": "true",
        "captive":  captive,
        "identified": identified,
        "place_id": str(county_id),
        "quality_grade": quality_grade,
        "order": "desc",
        "order_by": "count",
        "rank": rank,
        "acc_below": acc_below,
        "page": page,
        "per_page": per_page,
        "photos": photos,
        "fields": "all" #"(taxon:(name:!t,rank:!t))",
            }
    if native is not None:
        params["native"] = 'true' if native else 'false'
    if invasive is not None:
        params["native"] = 'false' if invasive else 'true'
    if endemic is not None:
        params["endemic"] = 'true' if endemic else 'false'
    if threatened is not None:
        params["threatened"] = threatened
    try:
        response = requests.get("https://api.inaturalist.org/v2/observations/species_counts", params=params)
        print(response.url) 
    except requests.exceptions.RequestException as e:
            print(f"Error occurred while making the request: {e}")
            return None
    return response

def write_csv(filename, data):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

#### Get the county geometry for Colorado from the ArcGIS API
def get_county_geometry():
    global COUNTY_GEOJSON

    if COUNTY_GEOJSON is None:
        response = requests.get("https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Census_Counties/FeatureServer/0/query?where=STATE_ABBR%3D%27CO%27&outFields=*&returnGeometry=true&outSR=4326&f=geojson")
        COUNTY_GEOJSON = response
    return COUNTY_GEOJSON

#### Get the county properties for Colorado from the ArcGIS API
def get_county_properties():
    global COUNTY_PROPERTIES
    if COUNTY_PROPERTIES is None:
        response = requests.get("https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Census_Counties/FeatureServer/0/query?where=STATE_ABBR%3D%27CO%27&outFields=*&returnGeometry=false&outSR=4326&f=geojson")
        COUNTY_PROPERTIES = response
    return COUNTY_PROPERTIES

def get_county_species_dataFrame():
    global COUNTY_SPECIES
    if COUNTY_SPECIES is None:
        COUNTY_SPECIES = pd.DataFrame(columns=['county_id','taxon_id'])
        COUNTY_SPECIES.set_index(['county_id','taxon_id'], inplace=True)
    return COUNTY_SPECIES
def get_county_species_result(county_id, filter_type="all", force_refresh=False):
    print(filter_type)
    global COUNTY_SPECIES
    county_species_df = get_county_species_dataFrame()
    total_pages = 1
    current_page = 1
    per_page = 500
    pageCount = 1
    switcher = {
        "native": (True, None, None),
        "invasive": (None, True, None),
        "endemic": (None, None, True),
        "all": (None, None, None)  }
    
    native, invasive, endemic = switcher.get(filter_type, (None, None, None))
    
    while total_pages >= current_page:
        
        response = get_County_Species_Counts(county_id, page=current_page, per_page=per_page, native=native, invasive=invasive, endemic=endemic)
        json_response = response.json()
        if(response is None):
            return
        print(json_response['total_results'])
        print(json_response['total_results'] // per_page + (1 if json_response['total_results'] % per_page > 0 else 0))
        
        total_pages = json_response['total_results'] // per_page + (1 if json_response['total_results'] % per_page > 0 else 0)
        current_page += 1
        
        results = json_response['results']
        
        row = []
        print(filter_type+"_species_count")
        if filter_type+"_species_count" not in county_species_df.columns:
            county_species_df[filter_type+"_species_count"] = np.nan

        for result in results:
            # print(county_species_df.head())
            county_species_df.loc[(county_id, result['taxon']['id']), filter_type+"_species_count"] = int(result['count'])
            # row.append({'county_id': county_id, 
            #             'taxonID': result['taxon']['id'],
            #             filter_type + "_species_count": result['count']
            #             })
        # county_species_df = pd.DataFrame.from_records(row)
        # COUNTY_SPECIES.county_species_df
        sleep(1)
    # append({'county_id': county_id, 'species_count': results['count'], 'preferred_establishment_means': results['preferred_establishment_means']}, ignore_index=True)


def add_county_species_counts_to_dataframe(df, force_refresh=False):
    df = get_county_dataframe(force_refresh=force_refresh)

    def get_species_count(row):
            try:
                get_county_species_result(county_id=row['id'], filter_type="all")
                sleep(1.5)  # Sleep for 1 second to avoid hitting the API rate limit
                get_county_species_result(county_id=row['id'], filter_type="native")
                sleep(1.5)  # Sleep for 1 second to avoid hitting the API rate limit
                get_county_species_result(county_id=row['id'], filter_type="invasive")
                sleep(1.5)  # Sleep for 1 second to avoid hitting the API rate limit
                get_county_species_result(county_id=row['id'], filter_type="endemic")

                species_counts = get_County_Species_Counts(county_id=row['id']).json()

                print(species_counts)
                sleep(1.5)  # Sleep for 1 second to avoid hitting the API rate limit
                # county_species_df = get_county_species_dataFrame()
                # county_species_df = pd.concat([county_species_df, pd.DataFrame({'county_id': [row['id']], 'species_count': [species_counts["total_results"]]})], ignore_index=True)

                # print(row['display_name'], species_counts["total_results"])
                return int(species_counts["total_results"])
            except Exception as e:
                # print(row)
                print(f"Error occurred while fetching species count for {row['display_name']} {row['id']}: {e.__class__.__name__}: {e}")
                sleep(5)  # Sleep for 5 seconds before retrying
                # get_species_count(row)  # Retry the request
                return None
    if 'species_count' not in df.columns or force_refresh:
        df['species_count'] = df.apply(lambda row: get_species_count(row), axis=1, result_type='expand')

#### Get the county dataframe for Colorado from the processed CSV file
def get_county_dataframe(force_refresh=False):
    global INAT_COUNTY_DATAFRAME
    if INAT_COUNTY_DATAFRAME is not None:
        return INAT_COUNTY_DATAFRAME
    import pandas as pd
    yearMonthDay = datetime.now().strftime("%Y-%m-%d")
    if not os.path.exists("data/processed/colorado_counties_"+yearMonthDay+".parquet") or force_refresh:
        d = get_iNat_county_data()
        df = pd.DataFrame(d)
        # df = pd.read_csv("data/processed/colorado_counties.csv",
                        # dtype={"fips": str})
        df['county_name'] = df.apply(lambda row: row['display_name'].split(',')[0], axis=1, result_type='expand')
        # def get_species_count(row):
        #     species_counts = get_County_Species_Counts(county_id=row['id'])
        #     sleep(1.5)  # Sleep for 1 second to avoid hitting the API rate limit
        #     print(row['display_name'], species_counts["total_results"])
        #     return species_counts["total_results"]
        # df['species_count'] = df.apply(lambda row: get_species_count(row), axis=1, result_type='expand')
        # df = add_county_species_counts_to_dataframe(df)
    else:
        print("Loading county dataframe from parquet file")
        df = pd.read_parquet("data/processed/colorado_counties_"+yearMonthDay+".parquet")
    if not os.path.exists("data/processed/colorado_counties_"+yearMonthDay+".parquet"):
        df.to_parquet("data/processed/colorado_counties_"+yearMonthDay+".parquet", index=False)
    print("Finished getting species counts for all counties")
    # for county in df.to_dict(orient='records'):
    #     species_counts = get_County_Species_Counts(county_id=county['id'])
    #     print(county['display_name'], species_counts["total_results"])
    #     sleep(1)  # Sleep for 1 second to avoid hitting the API rate limit
    #     county['species_count'] = species_counts["total_results"]
    INAT_COUNTY_DATAFRAME = df
    return INAT_COUNTY_DATAFRAME

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
    df['species_density_log'] = df.apply(lambda row: 0 if row['species_density'] == 0 else px.np.log(row['species_density']), axis=1, result_type='expand')
    df['species_per_person'] = df.apply(lambda row: int(row['species_count'])/float(row['population']), axis=1, result_type='expand')
    df['species_per_person_log'] = df.apply(lambda row: 0 if row['species_per_person'] == 0 else px.np.log(row['species_per_person']), axis=1, result_type='expand')
    df['species_per_person_demoniator_log'] = df.apply(lambda row: 0 if row['species_per_person'] == 0 else int(row['species_count'])/px.np.log(float(row['population'])), axis=1, result_type='expand')
    return df 

def get_iNat_county_data():
    global INAT_COUNTY_DATA
    if INAT_COUNTY_DATA is not None:
        return INAT_COUNTY_DATA
    if os.path.exists("data/processed/colorado_counties.csv"):
        print("File exists")
        counties = []
        with open('data/processed/colorado_counties.csv', 'r') as files:
            reader = csv.DictReader(files)
            for row in reader:
                counties.append(row)
    else:
        counties = get_USA_State_Counties(id=INAT_COLORADO_ID)
        write_csv("data/processed/colorado_counties.csv", counties)
    counties.sort(key=lambda x: x['display_name'], reverse=False)

    INAT_COUNTY_DATA = counties
    return INAT_COUNTY_DATA



def main():
    get_iNat_county_data()
    print("Got counties data, now plotting test")
    print("Got counties shape data, now plotting test")
    
    df = get_county_dataframe()
    df = add_county_species_counts_to_dataframe(df, force_refresh=True)
    print(df.head())
    df = get_species_density()
    import plotly.express as px
    print("Got counties data, now plotting Species Counts")
    print(df['species_count'].head())
    fig = px.choropleth_map(df, geojson=get_county_geometry().json(),featureidkey='properties.NAME', locations='county_name', color='species_count',
                            color_continuous_scale="Viridis",
                            #range_color=(0, 12),
                            map_style="carto-positron",
                            zoom=3, center = {"lat": 37.0902, "lon": -95.7129},
                            opacity=0.5,
                            labels={'species_per_person_demoniator_log':'Species Per Person D (Log)','species_per_person_log':'Species Per Person (Log)','species_per_person':'Species Per Person','species_density':'Species Density','species_density_per_sq_mi':'Species Density per Sq Mi','species_density_log':'Species Density (Log) '}
                            )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()




if __name__ == "__main__":
    main()