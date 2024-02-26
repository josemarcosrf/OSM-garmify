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



garmify-osm:
	# 	https://www.mkgmap.org.uk/download/mkgmap.html
	echo "🗺️ OSM file: $${osmfile:?}"
	echo "📂 Saving to: $${outdir:?}"
	java -Xmx512M -jar tools/mkgmap/mkgmap.jar \
		--unicode \
		--max-jobs=4 \
		--name-tag-list=name:en \
		--gmapsupp $${osmfile} \
		--output-dir=$${outdir}


garmify-velomap:
	# 	https://www.mkgmap.org.uk/download/mkgmap.html
	echo "🧲 Grouping files from $${dir:?} with file regex: $${fileregex:?}"
	echo "🪛 (description file: $${mdxfile:?} | Style file: $${typfile:?})"
	echo "📂 Saving to: $${outdir:?}"
	files=$$(find $${dir} -type f -regex $${fileregex})
	java -Xmx512M -jar tools/mkgmap/mkgmap.jar \
		--gmapsupp $${files} \
		--description=$${mdxfile} \
		--style-file=$${typfile} \
		--family-name=velomap \
		--max-jobs=4 \
		--output-dir=$${outdir}
