.PHONY: download-gmt garmify-velomap
.SILENT: download-gmt garmify-velomap


.ONESHELL:
extract-pois:
	# Extracts all POIs from a given .osm.pbf file
	# -
	# E.g.:
	# make extract-pois \
	# 	pbf_file=./data/OSM/afghanistan-latest.osm.pbf \
	# 	outfile=afghanistan-POIs.csv
	java -Xmx4g -jar ./tools/osmpois.jar \
		-ph \
		-of $${outfile}  \
		$${pbf_file}


split-osm:
	# Splits a .pbf or .osm file into smaller map tiles
	# -
	# requires: https://www.mkgmap.org.uk/doc/splitter.html
	echo "🗺️  OSM / PBF file: $${mapfile:?}"
	echo "📂 Saving to: $${outdir:?}"
	java -Xmx5G -jar tools/splitter/splitter.jar \
		--keep-complete=true \
		--output=pbf \
		--output-dir=$${outdir} \
		$${mapfile}


garmify-osm:
	# Combines and converts a collections of .pbf or .osm map files
	# into a Garmin compatible .img file (gmapsupp)
	# -
	# requires: https://www.mkgmap.org.uk/download/mkgmap.html
	files=$$(find $${dir:?} -type f -iname $${name:?})
	echo "🗺️  OSM / PBF files: $${files}"
	echo "📂 Saving to: $${outdir:?}"
	java -Xmx5G -jar tools/mkgmap/mkgmap.jar \
		--name-tag-list=name:en,int_name,name,place_name,loc_name \
		--mapname=$$(shuf -i 10000000-99999999 -n 1) \
		--unicode \
		--max-jobs=4 \
		--keep-going \
		--route \
    	--remove-short-arcs \
		--output-dir=$${outdir} \
		--gmapsupp $${files}

