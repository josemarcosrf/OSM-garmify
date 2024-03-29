# OSMaps to Garmin

This is just a collection of scripts and utilities to easy create Garmin-compatible maps form open-sources.

## Requirements

 - Python 3.8+
 - [mkgmap](https://www.mkgmap.org.uk/download/mkgmap.html)
 - [mkgmap splitter](https://www.mkgmap.org.uk/doc/splitter.html)
 - [GMapTool](https://www.gmaptool.eu/en/content/linux-version)


## How To

1. Run: `./download_tools.sh`
2. See below


<details>
  <summary>OSM</summary>

### OSM

After download a country .pbf map file from [geofabrik](https://download.geofabrik.de/)
an .img map file can be created by for example:

```bash
# Split the .pbf file into smaller ones
make split-osm mapfile=data/OSM/azerbaijan-latest.osm.pbf outdir=data/OSM/azerbaijan

# Combine into a Garmin .img file
make garmify-osm dir=data/OSM/azerbaijan name='6*.osm.pbf' outdir=data/OSM/azerbaijan
```

Alternatively, place as many .pbf files in `data/OSM/` as `data/OSM/<country>-latest.osm.pbf`. Update the script with the list of coutnries to
process and run:

```bash
bash do_all_osm.sh
```

</details>

<details>
  <summary>Velomap</summary>

### Velomap

After downloading some map files from [Velomap](https://www.velomap.org/),
for example to create a .img using a 10 meter contour line and esyvelo style:


```bash
make garmify-velomap \
    dir=data/Velo/Alps \
    fileregex='.*[67].*\.img' \
    typfile=data/Velo/Alps/esyvalp.TYP \
    mdxfile=data/Velo/Alps/mapset10.mdx
```

</details>

## A note on OSM files

In the context of OSM (OpenStreetMap), the .typ, .mdx, .tdb, and .img files are used for storing map data and style information. Here's a brief description of each file type:

- **.typ**: This file contains style information used for the display of the map elements, such as symbols for POIs, lines for roads, and area fill patterns for rivers or other areas[2](https://www.gpspower.net/garmin-tutorials/353310-basecamp-installing-free-desktop-map.html).
- **.mdx**: This is a kind of search index that describes the relations between regional maps. It is used by MapSource and BaseCamp[2](https://www.gpspower.net/garmin-tutorials/353310-basecamp-installing-free-desktop-map.html).
- **.tdb**: This is an index file used by MapSource and BaseCamp to decide which .img files belong to the map. It is mandatory for processing the map in MapSource and BaseCamp[2](https://www.gpspower.net/garmin-tutorials/353310-basecamp-installing-free-desktop-map.html).
- **.img**: These files are mandatory and contain map data. They include the base map, map segments (tiles), and optional features like search indexes[2](https://www.gpspower.net/garmin-tutorials/353310-basecamp-installing-free-desktop-map.html).

These files are used in Garmin's mapping software and devices to store and display map data and style information from OpenStreetMap and other sources


## Map sources

 - [Garmin.OpenTopo](https://garmin.opentopomap.org/) - issues with label name encoding

 - [extract.bbbike](https://extract.bbbike.org/) - Also available in [regions](https://download3.bbbike.org/osm/garmin/region/)

 - [geofabrik](https://download.geofabrik.de/) - Full OSM data for several contries & continents

 - [freizeitkarte-osm](http://www.freizeitkarte-osm.de/)

 - [openstreetmap Planet](https://wiki.openstreetmap.org/wiki/Planet.osm#Downloading)

 - [Velomap](https://www.velomap.org/)

