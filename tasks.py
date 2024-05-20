import glob
import os
import random
import shutil
import tempfile
import zipfile

import click
import wget
from invoke import Collection, UnexpectedExit, task
from tqdm.rich import tqdm


def _to_bullet_list(str_list):
    return "\n - " + "\n - ".join(str_list)


@task(
    help={
        "pbf_file": "mapfile to extract POIs from",
        "outfile": "CSV file to export POIs",
    }
)
def extract_pois(
    ctx, pbf_file: str, outfile: str, osmpois_jar: str = "./tools/osmpois.jar"
):
    """Extracts all POIs from a given *.osm.pbf file

    E.g.:
    invoke extract-pois \
        pbf_file=./data/OSM/afghanistan-latest.osm.pbf \
        outfile=afghanistan-POIs.csv
    """
    print("Extracting POIs")
    ctx.run(f"java -Xmx4g -jar {osmpois_jar} -ph -of {outfile} {pbf_file}")
    print("✅ Done!")


@task(
    help={
        "mapfile": ".pbf or .img to split",
        "outdir": "output directory",
        "splitter_jar": "Path to splitter jar file",
    }
)
def split_osm(
    ctx, mapfile: str, outdir: str, splitter_jar: str = "./tools/splitter/splitter.jar"
):
    """Splits a .pbf or .osm file into smaller map tiles
    requires: Java & https://www.mkgmap.org.uk/doc/splitter.html
    """
    print(f"🗺️  OSM / PBF file: {mapfile}")
    print(f"📂 Saving splits to: {outdir}")
    ctx.run(
        f"java -Xmx2G -jar {splitter_jar} "
        "--keep-complete=true "
        "--output=pbf "
        f"--output-dir={outdir} "
        f"{mapfile} "
    )
    print("✅ Done!")


@task(
    help={
        "in_dir": "Input directory where to look for .pbf or .img files",
        "outdir": "output directory",
        "glob_pattern": "File pattern-name to look for map files to combine",
        "recursive": "If True, look recursively for split map files to combine",
        "n_jobs": "Max num. of parallel jobs for mkgmap",
    }
)
def garmify_osm(
    ctx,
    in_dir: str,
    outdir: str,
    glob_pattern: str = "6*.pbf",
    recursive: bool = False,
    random_mapname: bool = False,
    n_jobs: int = 4,
    mkgmap_jar: str = "./tools/mkgmap/mkgmap.jar",
):
    """Combines and converts a collections of .pbf or .osm map files
    into a Garmin compatible .img file (gmapsupp)
    -
    requires: https://www.mkgmap.org.uk/download/mkgmap.html
    """
    files = glob.glob(os.path.join(in_dir, glob_pattern), recursive=recursive)
    print(f"🗺️  OSM / PBF files:{_to_bullet_list(files)}")
    print(f"📂 Saving resulting img map to: {outdir}")
    cmd = (
        f"java -Xmx2G -jar {mkgmap_jar} "
        "--name-tag-list=name:en,int_name,name,place_name,loc_name "
        "--unicode "
        "--keep-going "
        "--route "
        "--remove-short-arcs "
        f"--max-jobs={n_jobs} "
        f"--output-dir={outdir} "
        f"--gmapsupp {' '.join(files)}"
    )

    if random_mapname:
        cmd += f" --mapname={random.randint(10000000, 99999999)} "

    ctx.run(cmd)
    print("✅ Done!")


@task(
    help={
        "continent": "The continent name from which to download country maps",
        "countries": "Comma separated list of countries to compose a map from",
        "workdir": "Directory to download and create resulting map files",
    }
)
def garmify_geofabrik(ctx, continent: str, countries: str, workdir: str = "data/OSM"):
    """Creates a Garmin compatible map of the given countries based on
    map downlaods from Geofabrik.

    Note that for now it is limited to countries in the same Continent!

    Args:
        countries (list[str]): Comma separated list of countries to download.
        Example:
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
    """
    country_list = countries.split(",")
    print(f"List of countries:{_to_bullet_list(country_list)}")
    os.makedirs(workdir, exist_ok=True)

    continent = continent.lower()
    for country in country_list:
        country = country.lower()
        print(f"🪛  Processing country {country}")

        country_dir = os.path.join(workdir, country)
        map_pbf_file = os.path.join(country_dir, f"{country}-latest.osm.pbf")

        if not os.path.exists(map_pbf_file):
            os.makedirs(country_dir, exist_ok=True)
            country_url = (
                f"https://download.geofabrik.de/{continent}/{country}-latest.osm.pbf"
            )
            print(f"⏳️ Downloading country '{country}'")
            wget.download(country_url, out=map_pbf_file)

            print("✂️ Splitting...")
            split_osm(ctx, mapfile=map_pbf_file, outdir=country_dir)

    print("🗺️  Combining...")
    garmify_osm(
        ctx,
        in_dir=workdir,
        glob_pattern="**/6*.pbf",
        outdir=workdir,
        recursive=True,
        random_mapname=True,
    )

    img_fname = "_".join(c[:2] for c in country_list) + "_osm_geofabrik.img"
    print(f"🔀 Moving and renaming resulting map 👉 {img_fname}")
    shutil.move(
        os.path.join(workdir, "gmapsupp.img"),
        os.path.join(workdir, img_fname),
    )
    # shutil.rmtree(country_dir)
    print(f"✅ '{countries}' Done!")


@task(
    help={
        "input_dir": "Directory containing opentopo zipfiles",
        "country": "Name of the country to which download the map",
        "gmap_tool": "path the gmap. Defaults to ./gmt",
    }
)
def otm_xmerge(ctx, input_dir: str, country: str, gmap_tool: str = "./gmt"):
    """Given a directory of .zip files containing .img (Garmin) map files
    from https://garmin.opentopomap.org/, extracts and merges
    the map and countour files into a single map file ready to use in
    Garmin devices.

    Requires GMapTool: https://www.gmaptool.eu/en/content/linux-version
    """
    map_zipfile = os.path.join(input_dir, f"otm-{country}.zip")
    contour_zipfile = os.path.join(input_dir, f"otm-{country}-contours.zip")

    if not os.path.exists(map_zipfile):
        print(f"❌ 📂 Couldn't find '{map_zipfile}'")
        return

    if not os.path.exists(contour_zipfile):
        print(f"❌ 📂 Couldn't find '{contour_zipfile}'")
        return

    print(f"📤️ Extracting '{map_zipfile}'")
    map_img = f"otm-{country}.img"
    with zipfile.ZipFile(map_zipfile, "r") as zf:
        zf.extract(member=map_img, path=input_dir)

    print(f"📤️ Extracting '{contour_zipfile}'")
    contour_img = f"otm-{country}-contours.img"
    with zipfile.ZipFile(contour_zipfile, "r") as zf:
        zf.extract(member=contour_img, path=input_dir)

    # Write all the extracted files in a tmp txt file
    outname = f"{country}_otm_contours.img"
    with tempfile.NamedTemporaryFile("w", suffix=".txt") as fp:
        fp.write(os.path.join(input_dir, map_img) + "\n")
        fp.write(os.path.join(input_dir, contour_img) + "\n")
        fp.seek(0)

        # Compose the gmt command
        cmd = " ".join(
            [gmap_tool, "-j", "-o", os.path.join(input_dir, outname), "-@", fp.name]
        )
        print(f"🖥️ CMD: {' '.join(cmd)}")
        if click.confirm("\n👉️ Continue with the above command? "):
            print(f"📦️ Writing final map .img file: '{outname}'")
            ctx.run(cmd)


@task(
    help={
        "input_dir": "Directory containing opentopo zipfiles",
        "output_name": "Output name for the .img file",
        "gmap_tool": "path the gmap. Defaults to ./gmt",
    }
)
def bbbike_xmerge(ctx, input_dir: str, output_name: str, gmap_tool: str = "./gmt"):
    """Given a directory of .zip files containing .img (Garmin) map files
    from https://extract.bbbike.org/, extracts and creates
    a single map file ready to use in Garmin devices.

    Requires GMapTool: https://www.gmaptool.eu/en/content/linux-version
    """
    files = glob.glob(os.path.join(input_dir, "*.zip"))

    nfiles = []
    pbar = tqdm(files, total=len(files))
    for fpath in pbar:
        # parse the zip file name to figure the map type
        country = os.path.split(fpath)[-1].split(".")[0]
        fmt, src, encoding = os.path.split(fpath)[-1].split(".")[2].split("-")

        # Extract if file not present
        nfile = os.path.join(input_dir, f"{country}_{fmt}_{src}.img")
        nfiles.append(nfile)
        if os.path.exists(nfile):
            continue

        pbar.write(f"📤️ Extracting '{country}'")
        with zipfile.ZipFile(fpath, "r") as zf:
            efile = zf.extract(
                member=f"{country}-{fmt}-{src}-{encoding}/gmapsupp.img",
                path=input_dir,
            )
            os.rename(efile, nfile)

    # Write all the extracted files in a tmp txt file
    outname = output_name + ".img" if not output_name.endswith(".img") else output_name
    with tempfile.NamedTemporaryFile("w", suffix=".txt") as fp:
        fp.write("\n".join(nfiles))
        fp.seek(0)

        # Compose the gmt command
        cmd = " ".join(
            [gmap_tool, "-j", "-o", os.path.join(input_dir, outname), "-@", fp.name]
        )
        print(f"🖥️ CMD: {' '.join(cmd)}")
        if click.confirm("\n👉️ Continue with the above command? "):
            print(f"📦️ Writing final map .img file: '{outname}'")
            ctx.run(cmd)
