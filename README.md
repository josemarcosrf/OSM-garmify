# OSMaps to Garmin

This is just a collection of scripts and utilities to easy create Garmin-compatible maps form open-sources.


## A note on OSM files

In the context of OSM (OpenStreetMap), the .typ, .mdx, .tdb, and .img files are used for storing map data and style information. Here's a brief description of each file type:

- **.typ**: This file contains style information used for the display of the map elements, such as symbols for POIs, lines for roads, and area fill patterns for rivers or other areas[2](https://www.gpspower.net/garmin-tutorials/353310-basecamp-installing-free-desktop-map.html).
- **.mdx**: This is a kind of search index that describes the relations between regional maps. It is used by MapSource and BaseCamp[2](https://www.gpspower.net/garmin-tutorials/353310-basecamp-installing-free-desktop-map.html).
- **.tdb**: This is an index file used by MapSource and BaseCamp to decide which .img files belong to the map. It is mandatory for processing the map in MapSource and BaseCamp[2](https://www.gpspower.net/garmin-tutorials/353310-basecamp-installing-free-desktop-map.html).
- **.img**: These files are mandatory and contain map data. They include the base map, map segments (tiles), and optional features like search indexes[2](https://www.gpspower.net/garmin-tutorials/353310-basecamp-installing-free-desktop-map.html).

These files are used in Garmin's mapping software and devices to store and display map data and style information from OpenStreetMap and other sources


## Map sources

 - [Garmin.bbbike](https://extract.bbbike.org/) (ready [bbbike regions](https://download3.bbbike.org/osm/garmin/region/)
 - [Velomap](https://www.velomap.org/)

