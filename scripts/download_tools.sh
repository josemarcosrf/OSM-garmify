# Adjust to latest version (see www.mkgmap.org.uk)
MKGMAP="mkgmap-r4919"

# Adjust to latest version (see https://www.mkgmap.org.uk/download/splitter.html)
SPLITTER="splitter-r654" 

TOOLS_DIR="tools"

mkdir -p $TOOLS_DIR
cd $TOOLS_DIR

if [ ! -d "mkgmap" ]; then
    echo "⌛️ Downloading mkgmap"
    wget "http://www.mkgmap.org.uk/download/${MKGMAP}.zip"
    unzip "${MKGMAP}.zip"
    mv ${MKGMAP} mkgmap
else
    echo "✅ ${MKGMAP} already download!"
fi


if [ ! -d "splitter" ]; then
    echo "⌛️ Downloading splitter"
    wget "http://www.mkgmap.org.uk/download/${SPLITTER}.zip"
    unzip "${SPLITTER}.zip"
    mv ${SPLITTER} splitter
else
    echo "✅ ${SPLITTER} already download!"
fi

if [ ! -d "osmpois.jar" ]; then
    echo "⌛️ Downloading OSM-POIs extractor"
    wget "https://github.com/MorbZ/OsmPoisPbf/releases/download/v1.2/osmpois.jar"
else
    echo "✅ osmpois.jar already download!"
fi


cd -

mkdir -p data
cd data

if stat --printf='' bounds/bounds_*.bnd 2> /dev/null; then
    echo "✅ bounds already downloaded"
else
    echo "⌛️ Downloading bounds"
    rm -f bounds.zip  # just in case
    wget "http://osm2.pleiades.uni-wuppertal.de/bounds/latest/bounds.zip"
    unzip "bounds.zip" -d bounds
fi


if stat --printf='' sea/sea_*.pbf 2> /dev/null; then
    echo "✅ sea already downloaded"
else
    echo "⌛️ Downloading sea"
    rm -f sea.zip  # just in case
    wget "http://osm2.pleiades.uni-wuppertal.de/sea/latest/sea.zip"
    unzip "sea.zip" -d sea
fi

cd -

