#!/bin/bash

set -e

countries=(
    afghanistan
    armenia
    azerbaijan
    india
    iran
    kazakhstan
    kyrgyzstan
    nepal
    pakistan
    tajikistan
    turkmenistan
    uzbekistan
)

printf '%s\n' "${countries[@]}"

WDIR="data/OSM"
mkdir -p $WDIR

for country in "${countries[@]}"; do

    if [ ! -f "${WDIR}/${country}-latest.osm.pbf" ]; then
        echo "⏳️ Downloading country ${country}"
        wget "https://download.geofabrik.de/asia/${country}-latest.osm.pbf" -P $WDIR
    fi

    echo "🪛 Processing country ${country}"
    echo "✂️ Splitting..."
    make split-osm \
        mapfile=${WDIR}/${country}-latest.osm.pbf \
        outdir=${WDIR}/${country}
    
    echo "🗺️ Combining..."
    make garmify-osm \
        dir=${WDIR}/${country} \
            name='6*.osm.pbf' \
            outdir=${WDIR}/${country}

    mv "${WDIR}/${country}/gmapsupp.img" "${WDIR}/${country}_OSM_unicode.img"
    rm -r "${WDIR}/${country}"
done
