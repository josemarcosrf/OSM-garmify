

#!/bin/sh

set -e

countries=(
    tajikistan
    turkmenistan
    uzbekistan
)

printf '%s\n' "${countries[@]}"

for country in "${countries[@]}"; do
    echo "🪛 Processing country ${country}"
    echo "✂️ Splitting..."
    make split-osm \
        mapfile=data/OSM/${country}-latest.osm.pbf \
        outdir=data/OSM/${country}
    
    echo "🗺️ Combining..."
    make garmify-osm \
        dir=data/OSM/${country} \
            name='6*.osm.pbf' \
            outdir=data/OSM/${country}

    mv "data/OSM/${country}/gmapsupp.img" "data/OSM/${country}_OSM_unicode.img"
    rm -r "data/OSM/${country}"
done
