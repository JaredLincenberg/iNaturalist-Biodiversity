## raw/inaturalist_places.csv
Source: http://www.inaturalist.org/places/inaturalist-places.csv.zip
Downloaded: 2026-06-23
Notes: Updated weekly by iNaturalist. Columns include place_type, 
admin_level, ancestry (slash-separated lineage path, immediate-to-root).

## processed/colorado_counties.csv
Source: derived from raw/inaturalist_places.csv via src/get_counties.py
Filter: place_type=9, admin_level=20, ancestry contains place_id 34 (Colorado)