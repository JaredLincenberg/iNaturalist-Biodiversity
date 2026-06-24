import os

import requests
import csv

COLORADO_ID = 34
USA_ID = 1
NORTH_AMERICA_ID = 97394

def get_USA_State_Counties(id):
    counties = []
    with open('places/inaturalist-places.csv', 'r') as files:
        reader = csv.DictReader(files)
        for row in reader:
            if row['ancestry'] == str(NORTH_AMERICA_ID) + "/" + str(USA_ID) + "/" + str(id) and row['place_type'] == "9" and row['admin_level'] == "20":
                # print(row['display_name'], row['place_type'], row['admin_level'], row['id'])
                counties.append(row)
    return counties

def get_County_Observations(id):
    response = requests.get("https://api.inaturalist.org/v2/observations/species_counts?captive=false&identified=true&photos=true&verifiable=true&place_id=" + str(id) + "&quality_grade=research&order=desc&fields=species_guess%2Cobserved_on")
    return response.json()
def write_csv(filename, data):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
def check_bbox_area(county):
    county_bbox_area = county['bbox_area']
    calculated_area = (float(county['nelat']) - float(county['swlat'])) * (float(county['nelng']) - float(county['swlng']))
    return calculated_area

def main():
    print("Hello, World!")
    response = requests.get("https://api.inaturalist.org/v1/places/autocomplete?q=Denver&per_page=1")
    print(response.json())
    if os.path.exists("colorado_counties.csv"):
        print("File exists")
        counties = []
        with open('colorado_counties.csv', 'r') as files:
            reader = csv.DictReader(files)
            for row in reader:
                counties.append(row)
    else:
        counties =get_USA_State_Counties(id=34)
        print(len(counties))
        counties.sort(key=lambda x: x['display_name'], reverse=False)
        for county in counties:
            observations = get_County_Observations(id=county['id'])
            # print(observations["total_results"], county['display_name'], int(observations['total_results'])/float(county['bbox_area']))
            county['species_count'] = observations["total_results"]
            county['species_density'] = int(observations['total_results'])/float(county['bbox_area'])
        counties.sort(key=lambda x: x['species_density'], reverse=False)
        for county in counties:
            print(county['display_name'], county['species_count'], county['species_density'])
        write_csv("colorado_counties.csv", counties)
    for county in counties:
        # if abs(check_bbox_area(county) - float(county['bbox_area'])) > 0.0001:
        print("Area mismatch for county:", county['display_name'], "Calculated area:", check_bbox_area(county), "Reported area:", county['bbox_area'])
if __name__ == "__main__":
    main()