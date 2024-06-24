#!/bin/bash
countries=($(find ./data/OSM -mindepth 1 -type d))

for country_dir in "${countries[@]}"; do
    country=$(basename "$country_dir")
    inv garmify-osm -j 2 -a \
        -i ./data/DEM/otm-${country}-contours.img \
        -g './data/OSM/'"${country}"'/*.pbf' \
        -o ./data/OSM/${country}_osm+otm.img
done
