MKGMAP="mkgmap-r4917" # adjust to latest version (see www.mkgmap.org.uk)
SPLITTER="splitter-r653"

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
