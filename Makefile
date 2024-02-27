.PHONY: download-gmt garmify-velomap
.SILENT: download-gmt garmify-velomap


.ONESHELL:
download-gmt:
	mkdir -p tools
	cd tools
	wget https://www.gmaptool.eu/sites/default/files/lgmt08220.zip
	unzip lgmt08220.zip
	rm lgmt08220.zip *.txt
	cd -


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
		--unicode \
		--max-jobs=4 \
		--keep-going \
		--output-dir=$${outdir} \
		--gmapsupp $${files}


garmify-velomap:
	# Combines and converts a Velomap collection of .img, .typ and .mdx
	# files into a  Garmin compatible .img file (gmapsupp)
	# -
	# requires: https://www.mkgmap.org.uk/download/mkgmap.html
	echo "🧲 Grouping files from $${dir:?} with file regex: $${fileregex:?}"
	echo "🪛 (description file: $${mdxfile:?} | Style file: $${typfile:?})"
	echo "📂 Saving to: $${outdir:?}"
	files=$$(find $${dir} -type f -regex $${fileregex})
	java -Xmx5G -jar tools/mkgmap/mkgmap.jar \
		--gmapsupp $${files} \
		--description=$${mdxfile} \
		--style-file=$${typfile} \
		--family-name=velomap \
		--max-jobs=4 \
		--output-dir=$${outdir}
