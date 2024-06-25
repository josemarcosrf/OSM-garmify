import glob
import os
import random
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

import click
import wget
from invoke import task
from rich import print as rprint
from tqdm.rich import tqdm


def to_bullet_list(str_list):
    return "\n - " + "\n - ".join(str_list)


def print_cmd(cmd_str: str) -> None:
    print("⚙  Running command:")
    print(re.sub(r"--", r"\\\n  --", cmd_str))


@task
def download_geofabrik(ctx, continent: str, country: str, output_dir: Path | str):
    """Downloads a country's .pbf map file download.geofabrik.de

    Args:
        continent (str): Continent to download country maps of
        country (str): Country to download maps of
        output_dir (str): Directory where to store the map zipped files
    """
    # Create output dir if not present
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    map_name = f"{country}-latest.osm.pbf"
    download_url = f"https://download.geofabrik.de/{continent}/{map_name}"
    map_fpath = out_dir / map_name
    if not map_fpath.exists():
        print(f"⏳️ Downloading country '{country}'")
        wget.download(download_url, out=str(map_fpath))


@task
def download_otm(
    ctx, continent: str, country: str, output_dir: Path | str, delete_zips: bool = False
):
    """Downloads the country's map and contours zipped .img files from garmin.opentopomap.org

    Args:
        continent (str): Continent to download country maps of
        country (str): Country to download maps of
        output_dir (str): Directory where to store the map zipped files
    """

    def download_and_extract(map_name: str):
        zip_fpath = out_dir / f"{map_name}.zip"
        map_img_fpath = out_dir / f"{map_name}.img"
        if not map_img_fpath.exists():
            if not zip_fpath.exists():
                print(f"\n⏳️ Downloading '{map_name}'")
                wget.download(base_url + map_name + ".zip", out=str(zip_fpath))

            print(f"\n📤️ Extracting '{zip_fpath}'")
            with zipfile.ZipFile(str(zip_fpath), "r") as zf:
                zf.extract(member=map_name + ".img", path=str(out_dir))
        else:
            print(f"💫 Nothing to do; '{map_img_fpath}' already exists.")

        if delete_zips:
            zip_fpath.unlink()

        return map_img_fpath

    # Create output dir if not present
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    base_url = f"https://garmin.opentopomap.org/{continent}/{country}/"

    # Download the map file
    map_path = download_and_extract(f"otm-{country}")

    # Downlaod the contours file
    contours_path = download_and_extract(f"otm-{country}-contours")

    return map_path, contours_path


@task
def extract_pois(
    ctx, pbf_file: str, outfile: str, osmpois_jar: str = "./tools/osmpois.jar"
):
    """Extracts all POIs from a given *.osm.pbf file

    E.g.:
    invoke extract-pois \
        pbf_file=./data/OSM/afghanistan-latest.osm.pbf \
        outfile=afghanistan-POIs.csv

    Args:
        pbf_file (str): mapfile to extract POIs from
        outfile (str): CSV file to export POIs
        osmpois_jar (str, optional): _description_. Defaults to "./tools/osmpois.jar".
    """
    print("Extracting POIs")
    ctx.run(f"java -Xmx4g -jar {osmpois_jar} -ph -of {outfile} {pbf_file}")
    print("✅ Done!")


@task
def split(
    ctx,
    mapfile: Path | str,
    outdir: Path | str,
    splitter_jar: str = "./tools/splitter/splitter.jar",
):
    """Splits a .pbf or .osm file into smaller map tiles
    requires: Java & https://www.mkgmap.org.uk/doc/splitter.html

    Args:
        mapfile (Path | str): .pbf or .img to split
        outdir (Path | str): output directory
        splitter_jar (str, optional): Path to splitter jar file. Defaults to "./tools/splitter/splitter.jar".
    """
    print(f"✂️  Splitting  OSM / PBF file: {mapfile}")
    print(f"📂 Saving splits to: {outdir}")
    cmd = (
        f"java -Xmx2G -jar {splitter_jar} "
        f"{mapfile} "
        f"--mapid={random.randint(10000000, 99999999)} "
        f"--output-dir={outdir} "
        "--keep-complete=true "
        "--output=pbf "
    )
    print_cmd(cmd)
    ctx.run(cmd)
    print("✅ Done!")


@task
def garmify(
    ctx,
    output_file: str,
    input_files: str = "",
    glob_pattern: str = "./data/OSM/^[0-9]*.pbf",
    recursive: bool = False,
    random_mapname: bool = False,
    jobs: int = 4,
    mkgmap_jar: str = "./tools/mkgmap/mkgmap.jar",
):
    """Combines and converts a collections of .pbf or .osm map files
    into a Garmin compatible .img file (gmapsupp)
    -
    requires: https://www.mkgmap.org.uk/download/mkgmap.html

    Args:
        output_file (str): Output file path
        input_files (str, optional): Comma separated list of map files to combine. Defaults to "".
        glob_pattern (str, optional): File pattern-name to look for map files to combine. Defaults to "./data/OSM/^[0-9]*.pbf".
        recursive (bool, optional): If True, look recursively for split map files to combine. Defaults to False.
        random_mapname (bool, optional): Whther to use a randomly geenrated map name (8 digit number). Defaults to False.
        jobs (int, optional): Max num. of parallel jobs for mkgmap. Defaults to 4.
        mkgmap_jar (str, optional): Path to the mkgmap jar file. Defaults to "./tools/mkgmap/mkgmap.jar".
    """
    files = []
    if input_files:
        files += input_files.split(",")
    if glob_pattern:
        files += glob.glob(glob_pattern, recursive=recursive)

    if len(files) == 0:
        rprint(
            "💥 [red]No files found Error[/red]: Either a comma separated list of files "
            "OR a glob_pattern should be provided!"
        )
        return

    print(f"🗺️  OSM / PBF files:{to_bullet_list(files)}")
    print(f"📦 Total files to combine: {len(files)}")

    out_dir = Path(output_file).parent
    out_name = Path(output_file).name
    cmd = (
        f"java -Xmx2G -jar {mkgmap_jar} "
        "--name-tag-list=name:en,int_name,name,place_name,loc_name "
        "--unicode "
        "--keep-going "
        "--route "
        "--remove-short-arcs "
        "--remove-ovm-work-files "
        f"--max-jobs={jobs} "
        f"--output-dir={out_dir} "
        f"--gmapsupp {' '.join(files)}"
    )

    if random_mapname:
        cmd += f" --mapname={random.randint(10000000, 99999999)} "

    print_cmd(cmd)
    print(f"📂 Saving resulting img map as: {out_dir}")
    ctx.run(cmd)

    print(f"🔀 Moving and renaming resulting map 👉 {out_name}")
    shutil.move(
        out_dir / "gmapsupp.img",
        output_file,
    )
    print("✅ Done!")


@task
def garmify_geofabrik(
    ctx,
    continent: str,
    countries: str,
    workdir: str = "./data/OSM",
    split_maps: bool = False,
    merge_maps: bool = False,
):
    """Downloads and creates a Garmin compatible map of the given countries from Geofabrik.

    Note that for now it is limited to countries in the same Continent!

    Args:
        continent: The continent name from which to download country maps
        countries (list[str]): Comma separated list of countries to download.
                               e.g.: iran,turkmenistan,uzbekistan
        workdir (str): "Directory to download and create resulting map files.
        split_maps (bool): Whether to split after download (to avoid mem issues)
        merge_maps (bool): Whether to merge into a single map file
                           (required in some Garmin devices. e.g.: Edge 830)
    )
    """
    country_list = countries.split(",")
    print(f"List of countries:{to_bullet_list(country_list)}")
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)

    continent = continent.lower()
    for country in country_list:
        country = country.lower()
        country_dir = workdir / country
        print(f"🪛  Processing country {country}")

        # Maybe download and split into smaller map files to avoid mem issues.
        map_pbf_file = country_dir / f"{country}-latest.osm.pbf"
        if not map_pbf_file.exists():
            download_geofabrik(ctx, continent, country, country_dir)

        if split_maps:
            split(ctx, mapfile=map_pbf_file, outdir=country_dir)

    if merge_maps:
        if split_maps:
            glob_pattern = str(workdir / "**/[0-9]*.pbf")
        else:
            glob_pattern = str(workdir / "**/*-latest.osm.pbf")

        print("🗺️  Merging all maps...")
        img_fname = "+".join(c[:3].upper() for c in country_list) + "_osm_geofabrik.img"
        garmify(
            ctx,
            glob_pattern=glob_pattern,
            output_file=workdir / img_fname,
            recursive=True,
            random_mapname=True,
        )

    print(f"✅ '{countries}' Done!")


@task
def garmify_otm(
    ctx,
    continent: str,
    country: str,
    workdir: str,
    gmt_binary: str = "./tools/gmt",
):
    """Downloads, extracts and merges a country's map and countour files into a single Garmin map file.

    Requires GMapTool: https://www.gmaptool.eu/en/content/linux-version

    Args:
        continent (str): Name of the continent to download the map
        country (str): Name of the country to which download the map
        workdir (str): Directory containing opentopo zipfiles
        gmt_binary (str, optional): Path the gmap bin file. Defaults to "./tools/gmt".
    """
    workdir = Path(workdir)

    # Download and extract OTM map & contour files
    img_fpath, contours_fpath = download_otm(
        ctx, continent, country, workdir, delete_zips=True
    )

    with tempfile.NamedTemporaryFile("w", suffix=".txt") as fp:
        # Write all the extracted files in a tmp txt file for merging
        fp.write(str(img_fpath) + "\n")
        fp.write(str(contours_fpath) + "\n")
        fp.seek(0)

        # Compose the gmt command
        output_path = workdir / f"{country}_otm.img"
        cmd = " ".join([gmt_binary, "-j", "-o", str(output_path), "-@", fp.name])
        print_cmd(cmd)
        if click.confirm("\n👉️ Continue with the above command? "):
            print(f"📦️ Writing final map .img file: '{output_path}'")
            ctx.run(cmd)


@task
def bbbike_xmerge(
    ctx, input_dir: Path | str, output_name: Path | str, gmap_tool: str = "./tools/gmt"
):
    """Given a directory of .zip files containing .img (Garmin) map files
    from https://extract.bbbike.org/, extracts and creates
    a single map file ready to use in Garmin devices.

    Requires GMapTool: https://www.gmaptool.eu/en/content/linux-version

    Args:
        input_dir (Path | str): Directory containing opentopo zipfiles
        output_name (Path | str): Output name for the .img file
        gmap_tool (str, optional): Path the gmap. Defaults to ./tools/gmt. Defaults to "./tools/gmt".
    """
    input_dir = Path(input_dir)
    files = glob.glob(str(input_dir / "*.zip"))

    nfiles = []
    pbar = tqdm(files, total=len(files))
    for fpath in pbar:
        # parse the zip file name to figure the map type
        country = os.path.split(fpath)[-1].split(".")[0]
        fmt, src, encoding = os.path.split(fpath)[-1].split(".")[2].split("-")

        # Extract if file not present
        nfile = input_dir / f"{country}_{fmt}_{src}.img"
        nfiles.append(nfile)
        if nfile.exists():
            continue

        pbar.write(f"📤️ Extracting '{country}'")
        with zipfile.ZipFile(fpath, "r") as zf:
            efile = zf.extract(
                member=f"{country}-{fmt}-{src}-{encoding}/gmapsupp.img",
                path=str(input_dir),
            )
            os.rename(efile, str(nfile))

    # Write all the extracted files in a tmp txt file
    outname = output_name + ".img" if not output_name.endswith(".img") else output_name
    with tempfile.NamedTemporaryFile("w", suffix=".txt") as fp:
        fp.write("\n".join(nfiles))
        fp.seek(0)

        # Compose the gmt command
        cmd = " ".join([gmap_tool, "-j", "-o", str(input_dir / outname), "-@", fp.name])
        print(f"🖥️ CMD: {' '.join(cmd)}")
        if click.confirm("\n👉️ Continue with the above command? "):
            print(f"📦️ Writing final map .img file: '{outname}'")
            ctx.run(cmd)
