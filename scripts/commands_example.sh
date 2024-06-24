#!bin/bash

indir="${PWD}/data/OSM/"
outdir=${indir}/${country}
mapname=$(shuf -i 10000000-99999999 -n 1)

country="armenia"

mkdir -p "${outdir}"

# 1. --------- Split the .pbf tile files ---------
mapfile="${indir}/${country}-latest.osm.pbf"
java -Xmx1G -jar tools/splitter/splitter.jar \
    --keep-complete=true \
    --output=pbf \
    --output-dir="${outdir}" \
    ${mapfile}


# 2.a Combine the country's .pbf files into a single .img map file
files=$(find ${outdir} -type f -iname '*.pbf')
java -Xmx1G -jar tools/mkgmap/mkgmap.jar \
    --mapname=${mapname} \
    --country-name=${country} \
    --max-jobs=4 \
    --keep-going \
    --route \
    --remove-short-arcs \
    --remove-ovm-work-files \
    --gmapsupp ${files} \
    --output-dir="${outdir}"


# OR:
# 2.b. Combine all countries .pbf files into a single .img map file
files=$(find ${indir} -type f -iname '[0-9]*.pbf')
echo ${files} | tr ' ' "\n"
java -Xmx2G -jar tools/mkgmap/mkgmap.jar \
    --name-tag-list=name:en,int_name,name,place_name,loc_name \
    --unicode \
    --keep-going \
    --route \
    --remove-short-arcs \
    --remove-ovm-work-files \
    --max-jobs=4 \
    --gmapsupp ${files} \
    --mapname=${mapname} \
    --output-dir="${indir}"
