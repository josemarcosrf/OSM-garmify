import glob
import os
import subprocess
import tempfile
import zipfile

import click
from invoke import task
from tqdm.rich import tqdm


@task
def extract_pois(
    ctx,
):
    pass


@task(
    help={
        "mapfile": ".pbf or .img to split",
        "outdir": "output directory",
        "splitter_jar": "Path to splitter jar file",
    }
)
def split_osm(
    ctx, mapfile: str, outdir: str, splitter_jar: str = "tools/splitter/splitter.jar"
):
    """Splits a .pbf or .osm file into smaller map tiles
    requires: Java & https://www.mkgmap.org.uk/doc/splitter.html
    """
    print(f"🗺️  OSM / PBF file: ${mapfile}")
    print(f"📂 Saving to: ${outdir}")
    ctx.run(
        f"java -Xmx5G -jar {splitter_jar} "
        "--keep-complete=true "
        "--output=pbf "
        f"--output-dir={outdir} "
        f"{mapfile} "
    )


@task
def garmify_osm(
    ctx,
):
    pass


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
        cmd = [gmap_tool, "-j", "-o", os.path.join(input_dir, outname), "-@", fp.name]
        print(f"🖥️ CMD: {' '.join(cmd)}")
        if click.confirm("\n👉️ Continue with the above command? "):
            print(f"📦️ Writing final map .img file: '{outname}'")
            subprocess.run(cmd)


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
        cmd = [gmap_tool, "-j", "-o", os.path.join(input_dir, outname), "-@", fp.name]
        print(f"🖥️ CMD: {' '.join(cmd)}")
        if click.confirm("\n👉️ Continue with the above command? "):
            print(f"📦️ Writing final map .img file: '{outname}'")
            subprocess.run(cmd)
