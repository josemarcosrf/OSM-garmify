#!/bin/bash

build_country() {
    local country=$1
    echo "Building country: ${country}..."

    # Download OSM
    inv garmify-geofabrik asia ${country} -w ./data/OSM -s

    # Download DEM data
    inv garmify-otm asia ${country} -w ./data/DEM

    # Combine OSM + DEM
    inv garmify -j 2 -a \
        -i ./data/DEM/otm-${country}-contours.img \
        -g './data/OSM/'"${country}"'/[0-9]*.pbf' \
        -o ./data/${country}_osm+otm.img
}


# Define a list of central Asian countries
# opentopo has an issue with Asia base map files
countries=("iran" "turkmenistan" "uzbekistan" "tajikistan" "kyrgyzstan")

# Merges OTM contour files with Geofabrik OSM map files in the ./data directory
for country in "${countries[@]}"; do
    build_country "$country"
done

# Clean up all tmp files
find ./data -mindepth 1 -maxdepth 2 -iname '[0-9]*.img' -delete
