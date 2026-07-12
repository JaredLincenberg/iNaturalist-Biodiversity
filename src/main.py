from datetime import datetime
from functools import cache
import os
from time import sleep

import plotly
import requests
import csv
import plotly.express as px
from urllib.request import urlopen
import pandas as pd
import requests_cache      
import numpy as np
import plotly.graph_objects as go
requests_cache.install_cache('cache/inaturalist_cache', backend='sqlite', expire_after=10_000_000)

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

REQUEST_COUNT = 0
CACHE_HIT_COUNT = 0
CACHE_MISS_COUNT = 0

PLANTS_ANCESTRY_PATH = "48460/47126/"
ANIMALS_ANCESTRY_PATH = "48460/1/"
VERTBRATES_ANCESTRY_PATH = "48460/1/2/355675/"
ARTHROPODS_ANCESTRY_PATH = "48460/1/47120/"
# PLANTS_TAXON_ID = 47126
# ANIMALS = ['Aves', 'Mammalia', 'Reptilia', 'Amphibia', 'Actinopterygii', 'Chondrichthyes', 'Cephalaspidomorphi', 'Myxini']

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
    # List of Tuples, to keep the order of the parameters consistent
    params = [
        ("verifiable", "true"),
        ("captive", captive),
        ("identified", identified),
        ("place_id", str(county_id)),
        ("quality_grade", quality_grade),
        ("order", "desc"),
        ("order_by", "count"),
        ("rank", rank),
        ("acc_below", acc_below),
        ("page", page),
        ("per_page", per_page),
        ("photos", photos),
        ("fields", "all")  # "(taxon:(name:!t,rank:!t))",
    ]
    if native is not None:
        params.append(("native", 'true' if native else 'false'))
    if invasive is not None:
        params.append(("native", 'false' if invasive else 'true'))
    if endemic is not None:
        params.append(("endemic", 'true' if endemic else 'false'))
    if threatened is not None:
        params.append(("threatened", threatened))
    try:
        response = requests.get("https://api.inaturalist.org/v2/observations/species_counts", params=params)
        global REQUEST_COUNT
        REQUEST_COUNT += 1
        print(f"Request {REQUEST_COUNT}: {response.url}")
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
        # List of Tuples, to keep the order of the parameters consistent
        params = [
            ("where", "STATE_ABBR='CO'"),
            ("outFields", "*"),
            ("returnGeometry", "true"),
            ("outSR", "4326"),
            ("f", "geojson")
        ]
        response = requests.get("https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Census_Counties/FeatureServer/0/query", params=params)
        COUNTY_GEOJSON = response
    return COUNTY_GEOJSON

#### Get the county properties for Colorado from the ArcGIS API
def get_county_properties():
    global COUNTY_PROPERTIES
    if COUNTY_PROPERTIES is None:
        params = {
            "where": "STATE_ABBR='CO'",
            "outFields": "*",
            "returnGeometry": "false",
            "outSR": "4326",
            "f": "geojson"
        }  
        response = requests.get("https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Census_Counties/FeatureServer/0/query", params=params)
        COUNTY_PROPERTIES = response
    return COUNTY_PROPERTIES

def get_county_species_dataFrame():
    global COUNTY_SPECIES
    if COUNTY_SPECIES is None:
        COUNTY_SPECIES = pd.DataFrame(columns=['county_id','taxon_id'])
        COUNTY_SPECIES.set_index(['county_id','taxon_id'], inplace=True)
    return COUNTY_SPECIES
def get_taxonomy_data():
    global TAXONOMY_DATA
    if TAXONOMY_DATA is None:
        TAXONOMY_DATA = pd.DataFrame(columns=['taxon_id','name','rank','ancestry','iconic_taxon_name','iconic_taxon_id','preferred_common_name','wikipedia_url'])
        TAXONOMY_DATA.set_index(['taxon_id'], inplace=True)
    return TAXONOMY_DATA
def get_county_species_result(county_id,county_name, filter_type="all", force_refresh=False):
    print(filter_type, county_id, county_name)
    global COUNTY_SPECIES
    global TAXONOMY_DATA
    county_species_df = get_county_species_dataFrame()
    taxonomy_df = get_taxonomy_data()
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
        total_pages = json_response['total_results'] // per_page + (1 if json_response['total_results'] % per_page > 0 else 0)
        current_page += 1
        
        results = json_response['results']
        
        row = []
        # print(filter_type+"_species_count")
        if filter_type+"_species_count" not in county_species_df.columns:
            county_species_df[filter_type+"_species_count"] = np.nan

        for result in results:
            if result['taxon']['id'] not in taxonomy_df.index:
                taxonomy_df.loc[result['taxon']['id'], 'name'] = result['taxon']['name'] if 'name' in result['taxon'] else pd.NA
                taxonomy_df.loc[result['taxon']['id'], 'rank'] = result['taxon']['rank'] if 'rank' in result['taxon'] else pd.NA
                taxonomy_df.loc[result['taxon']['id'], 'ancestry'] = result['taxon']['ancestry'] if 'ancestry' in result['taxon'] else pd.NA
                taxonomy_df.loc[result['taxon']['id'], 'iconic_taxon_name'] = result['taxon']['iconic_taxon_name'] if 'iconic_taxon_name' in result['taxon'] else pd.NA
                taxonomy_df.loc[result['taxon']['id'], 'iconic_taxon_id'] = result['taxon']['iconic_taxon_id'] if 'iconic_taxon_id' in result['taxon'] else pd.NA
                taxonomy_df.loc[result['taxon']['id'], 'preferred_common_name'] = result['taxon']['preferred_common_name'] if 'preferred_common_name' in result['taxon'] else pd.NA
                taxonomy_df.loc[result['taxon']['id'], 'english_common_name'] = result['taxon']['english_common_name'] if 'english_common_name' in result['taxon'] else pd.NA
                taxonomy_df.loc[result['taxon']['id'], 'wikipedia_url'] = result['taxon']['wikipedia_url'] if 'wikipedia_url' in result['taxon'] else pd.NA
            else:
                pass
            county_species_df.loc[(county_id, result['taxon']['id']), filter_type+"_species_count"] = int(result['count'])
            county_species_df.loc[(county_id, result['taxon']['id']), "county_name"] = county_name
        if not response.from_cache:
            global CACHE_MISS_COUNT 
            CACHE_MISS_COUNT += 1
            print("From API")
            sleep(1)
        else:
            global CACHE_HIT_COUNT
            CACHE_HIT_COUNT += 1
            print("From Cache")


def add_county_species_counts_to_dataframe(df, force_refresh=False):
    df = get_county_dataframe(force_refresh=force_refresh)
    yearMonthDay = datetime.now().strftime("%Y-%m-%d")
    yearMonth = datetime.now().strftime("%Y-%m")
    if os.path.exists("data/processed/colorado_county_species_counts_"+yearMonthDay+".parquet") and os.path.exists("data/processed/taxonomy_data_"+yearMonth+".parquet") and not force_refresh:
        print("Loading county species counts from parquet file")
        df_county_species_df = pd.read_parquet("data/processed/colorado_county_species_counts_"+yearMonthDay+".parquet")
        print("Loading taxonomy data from parquet file")
        df_taxonomy_df = pd.read_parquet("data/processed/taxonomy_data_"+yearMonth+".parquet")
        global TAXONOMY_DATA
        TAXONOMY_DATA = df_taxonomy_df
    else:
        print("Getting county species counts from iNaturalist API")
        for df_row in df.itertuples():
            get_county_species_result(county_id=df_row.id, county_name=df_row.county_name, filter_type="all")
            get_county_species_result(county_id=df_row.id, county_name=df_row.county_name, filter_type="native")
            get_county_species_result(county_id=df_row.id, county_name=df_row.county_name, filter_type="invasive")
            get_county_species_result(county_id=df_row.id, county_name=df_row.county_name, filter_type="endemic")
        
        df_county_species_df = get_county_species_dataFrame()
        df_county_species_df.to_parquet("data/processed/colorado_county_species_counts_"+yearMonthDay+".parquet", index=True)
        df_taxonomy_df = get_taxonomy_data()
        df_taxonomy_df.to_parquet("data/processed/taxonomy_data_"+yearMonth+".parquet", index=True)
        print("Finished getting species counts for all counties. Saving to parquet file")
    
    # df_county_species_df.reset_index(inplace=True)
    # df_county_species_df = df_county_species_df[df_county_species_df['all_species_count'] > 2]
    print("df_county_species_df head:", df_county_species_df.head())
    df_county_species_taxonomy_df = pd.merge(df_county_species_df, df_taxonomy_df, left_on='taxon_id', right_index=True)
    # print("df_county_species_taxonomy_df head after merge:", df_county_species_taxonomy_df.head())
    # np.where()
    # df_county_species_taxonomy_df.where(df_county_species_taxonomy_df['ancestry'].str.startswith(PLANTS_ANCESTRY_PATH),)
    df_county_species_taxonomy_df = df_county_species_taxonomy_df.assign(plant_count=lambda x: np.where(x['ancestry'].str.startswith(PLANTS_ANCESTRY_PATH), x['all_species_count'], np.nan))
    df_county_species_taxonomy_df = df_county_species_taxonomy_df.assign(animal_count=lambda x: np.where(x['ancestry'].str.startswith(ANIMALS_ANCESTRY_PATH), x['all_species_count'], np.nan))
    df_county_species_taxonomy_df = df_county_species_taxonomy_df.assign(vertbrate_count=lambda x: np.where(x['ancestry'].str.startswith(VERTBRATES_ANCESTRY_PATH), x['all_species_count'], np.nan))
    df_county_species_taxonomy_df = df_county_species_taxonomy_df.assign(arthropod_count=lambda x: np.where(x['ancestry'].str.startswith(ARTHROPODS_ANCESTRY_PATH), x['all_species_count'], np.nan))
    df_county = df_county_species_taxonomy_df.groupby('county_id').agg({
        'all_species_count': 'count',
        'native_species_count': 'count',
        'invasive_species_count': 'count',
        'endemic_species_count': 'count',
        'plant_count': 'count',
        'animal_count': 'count',
        'vertbrate_count': 'count',
        'arthropod_count': 'count',
        'county_name': 'first'
    }).rename(columns={'plant_count': 'flora_species_count', 'animal_count': 'fauna_species_count', 'vertbrate_count': 'vertebrate_species_count', 'arthropod_count': 'arthropod_species_count'})
    return get_county_species_ratios(df_county)
def get_county_species_ratios(df_county):
    df_county = df_county.assign(flora_fauna_species_count=lambda x: x['flora_species_count'] + x['fauna_species_count'])
    df_county = df_county.assign(native_invasive_ratio=lambda x: x['native_species_count'] / x['invasive_species_count'].replace(0, np.nan))
    df_county = df_county.assign(native_all_ratio=lambda x: x['native_species_count'] / x['all_species_count'].replace(0, np.nan))
    df_county = df_county.assign(invasive_all_ratio=lambda x: x['invasive_species_count'] / x['all_species_count'].replace(0, np.nan))
    return df_county

def add_county_species_counts_to_dataframe_old(df, force_refresh=False):
    df = get_county_dataframe(force_refresh=force_refresh)

    def get_species_count(row):
            try:
                species_counts = get_County_Species_Counts(county_id=row['id']).json()
                # print(species_counts)
                sleep(1.5)  # Sleep for 1.5 second to avoid hitting the API rate limit

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
def get_map_buttons(df):
    hoverTemplate1 = "<b>%{location}</b><br>%{z:,} species"
    hoverTemplate2 = "<b>%{location}</b><br>%{z:,} native species<br> %{customdata[1]:.0%} of total<br>"
    hoverTemplate3 = "<b>%{location}</b><br>%{z:,} invasive species<br> %{customdata[1]:.0%} of total<br>"
    hoverTemplate4 = "<b>%{location}</b><br>%{z:,} flora species<br>"
    hoverTemplate5 = "<b>%{location}</b><br>%{z:,} fauna species<br>"
    hoverTemplate6 = "<b>%{location}</b><br>%{z:,} vertebrate species<br>"
    hoverTemplate7 = "<b>%{location}</b><br>%{z:,} arthropod species<br>"
    hoverTemplate8 = "<b>%{location}</b><br>%{z:,} flora + fauna species<br>"
    hoverTemplate9 = "<b>%{location}</b><br>%{z:,.2f} native/invasive ratio<br> %{customdata[0]:,} native to %{customdata[1]:,} invasive<br> Total species %{customdata[2]:,}<br>"

    button1 = go.layout.updatemenu.Button(label="All Species",
                   method="update",
                   args=[{
                         "z":[df['all_species_count']],
                         "hovertemplate": hoverTemplate1,
                         },
                       {"coloraxis": {"colorbar": {"title": {"text": "All Species Count"}}} }])
    print(df['native_all_ratio'].head())
    button2 = go.layout.updatemenu.Button(label="Native Species",
                   method="update",
                   args=[{
                       "z":[df['native_species_count']],
                       "customdata": [df[['all_species_count', 'native_all_ratio']].values],
                       "hovertemplate": hoverTemplate2},
                       {
                           "coloraxis": {"colorbar": {"title": {"text": "Native Species Count"}}} 
                        }
                   ])
    button3 = go.layout.updatemenu.Button(label="Invasive Species",
                   method="update",
                   args=[{
                       "z":[df['invasive_species_count']],
                       "customdata": [df[['all_species_count', 'invasive_all_ratio']].values],
                       "hovertemplate": hoverTemplate3},
                       {
                           "coloraxis": {"colorbar": {"title": {"text": "Invasive Species Count"}}}
                       }
                   ])
    button4 = go.layout.updatemenu.Button(label="Flora Species",
                   method="update",
                   args=[{
                       "z":[df['flora_species_count']],
                       "hovertemplate": hoverTemplate4},
                       {
                           "coloraxis": {"colorbar": {"title": {"text": "Flora Species Count"}}}
                       }
                   ])
    button5 = go.layout.updatemenu.Button(label="Fauna Species",
                   method="update",
                   args=[{
                       "z":[df['fauna_species_count']],
                       "hovertemplate": hoverTemplate5},
                       {
                           "coloraxis": {"colorbar": {"title": {"text": "Fauna Species Count"}}}
                       }
                   ])
    button6 = go.layout.updatemenu.Button(label="Vertebrate Species",
                   method="update",
                   args=[{
                       "z":[df['vertebrate_species_count']],
                       "hovertemplate": hoverTemplate6},
                       {
                           "coloraxis": {"colorbar": {"title": {"text": "Vertebrate Species Count"}}}
                       }
                   ])
    button7 = go.layout.updatemenu.Button(label="Arthropod Species",   
                   method="update",
                   args=[{
                       "z":[df['arthropod_species_count']],
                       "hovertemplate": hoverTemplate7},
                       {
                           "coloraxis": {"colorbar": {"title": {"text": "Arthropod Species Count"}}}
                       }
                   ])
    button8 = go.layout.updatemenu.Button(label="Flora + Fauna Species",
                   method="update",
                   args=[{
                       "z":[df['flora_fauna_species_count']],
                       "hovertemplate": hoverTemplate8},
                       {
                           "coloraxis": {"colorbar": {"title": {"text": "Flora + Fauna Species Count"}}}
                       }
                   ])
    button9 = go.layout.updatemenu.Button(label="Native/Invasive Ratio",
                   method="update",
                   args=[{
                       "z":[df['native_invasive_ratio']],
                       "customdata": [df[['native_species_count', 'invasive_species_count', 'all_species_count']].values],
                       "hovertemplate": hoverTemplate9},
                       {
                           "coloraxis": {"colorbar": {"title": {"text": "Native/Invasive Ratio"}}}
                       }
                   ])
    return [button1, button2, button3, button4, button5, button6, button7, button8, button9]
def get_color_scale_for_button():
    ### NOTE: Color scales to do not error on typos and will default.

#     print(px.colors.sequential.__dict__.keys())
#     print(type(px.colors.sequential.Viridis))
#     print(type(px.colors.sequential.__name__))
#     print(type(px.colors.sequential.swatches))
#     print(px.colors.named_colorscales())
    colorscale_buttons = [
        dict(label="Blues", method="relayout", args=[{"coloraxis.colorscale": "Blues"}]),
        dict(label="Viridis", method="relayout", args=[{"coloraxis.colorscale": "Viridis"}]),
        dict(label="Cividis", method="relayout", args=[{"coloraxis.colorscale": "Cividis"}]),
    ]
    return colorscale_buttons


def main():
    get_iNat_county_data()
    print("Got counties data, now plotting test")
    print("Got counties shape data, now plotting test")
    # print(plotly.express.colors.sequential.__dir__())
    df = get_county_dataframe()
    df = add_county_species_counts_to_dataframe(df, force_refresh=False)
    print(df.head())
    taxon = get_taxonomy_data()
    print(taxon.head())
    # df = get_species_density()
    import plotly.express as px
    print("Got counties data, now plotting Species Counts")
    print(df['invasive_species_count'].head())
    print(f'requests: {REQUEST_COUNT}, Cache Hits: {CACHE_HIT_COUNT}, Cache Misses: {CACHE_MISS_COUNT}')

    fig = px.choropleth_map(df, geojson=get_county_geometry().json(),featureidkey='properties.NAME', locations='county_name', color='all_species_count',
                            color_continuous_scale="Viridis",
                            #range_color=(0, 12),
                            map_style="carto-darkmatter",
                            zoom=6, center = {"lat": 39.0, "lon": -105.0},
                            opacity=0.5,
                            )

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    # title = px.layout.Title(text="Colorado County Species Counts", x=0.5, font=dict(size=24, color='black', family="Arial, sans-serif"))        
    fig.update_layout(title=dict(text='Colorado County Species Counts', 
                      x=0.5, font=dict(size=24, color='black', family="Arial, sans-serif")),
                      updatemenus=[dict(type="buttons", direction="right", y=1.15, xanchor="left", x=0.05, buttons=get_map_buttons(df),showactive=True),
                                   dict(type="dropdown", direction="right", y=1.05, xanchor="left", x=0.05, buttons=get_color_scale_for_button(),showactive=True)]
                      )
    print("Map Buttons:")
    print(get_map_buttons(df)[0].args)
    print(get_map_buttons(df)[1].args)
    button1_trace_args, button1_layout_args = get_map_buttons(df)[0].args
    fig.update_traces(z=button1_trace_args['z'][0], hovertemplate=button1_trace_args.get('hovertemplate'))
    fig.update_layout(**button1_layout_args)
    fig.show()




if __name__ == "__main__":
    main()