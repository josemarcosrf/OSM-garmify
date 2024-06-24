#!/bin/bash

# # Check all the country directories with split .pbf files in ./data/OSM
# countries=($(find ./data/OSM -mindepth 1 -type d))

# TODO: Input a list of countries...

# Merges OTM contour files with Geofabrik OSM map files in the ./data directory
for country_dir in "${countries[@]}"; do
    country=$(basename "$country_dir")

    # TODO: Download OSM (check this works as intended)
    inv download-geofabrik asia ${country} -o ./data/OSM

    # TODO: Split OSM
    inv split-osm ...

    # Download DEM data
    inv garmify-otm asia ${country} -w ./data/DEM

    # Combine OSM + DEM
    inv garmify-osm -j 2 -a \
        -i ./data/DEM/otm-${country}-contours.img \
        -g './data/OSM/'"${country}"'/*.pbf' \
        -o ./data/${country}_osm+otm.img
done

# TODO: Combine several countries?

# Clean up all tmp files
find ./data -mindepth 1 -maxdepth 1 -iname '[0-9]*.img' -delete
