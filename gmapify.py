import glob
import os
import subprocess
import tempfile
import zipfile

import click
from tqdm.auto import tqdm


@click.group()
def cli():
    pass


@cli.command("otm-xmerge")
@click.argument("input_dir")
@click.argument("country")
@click.option("-g", "--gmap-tool", default="./gmt")
def otm_xmerge(input_dir:str, country:str, gmap_tool:str):
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
    with zipfile.ZipFile(map_zipfile, 'r') as zf:
        zf.extract(member=map_img, path=input_dir)

    print(f"📤️ Extracting '{contour_zipfile}'")
    contour_img = f"otm-{country}-contours.img"
    with zipfile.ZipFile(contour_zipfile, 'r') as zf:
        zf.extract(member=contour_img, path=input_dir)

    # Write all the extracted files in a tmp txt file
    outname = f"{country}_otm_contours.img"
    with tempfile.NamedTemporaryFile("w", suffix=".txt") as fp:
        fp.write(os.path.join(input_dir, map_img) + "\n")
        fp.write(os.path.join(input_dir, contour_img) + "\n")
        fp.seek(0)

        # Compose the gmt command
        cmd = [
            gmap_tool, "-j", "-o", os.path.join(input_dir, outname), "-@", fp.name
        ]
        print(f"🖥️ CMD: {' '.join(cmd)}")
        if click.confirm("\n👉️ Continue with the above command? "):
            print(f"📦️ Writing final map .img file: '{outname}'")
            subprocess.run(cmd)


@cli.command("bbbike-xmerge")
@click.argument("input_dir")
@click.option("-g", "--gmap-tool", default="./gmt")
@click.option("-n", "--name", default="out.img")
def bbbike_xmerge(input_dir:str, gmap_tool:str, name:str):
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
        with zipfile.ZipFile(fpath, 'r') as zf:
            efile = zf.extract(
                member=f"{country}-{fmt}-{src}-{encoding}/gmapsupp.img",
                path=input_dir,
            )
            os.rename(efile, nfile)

    # Write all the extracted files in a tmp txt file
    outname = name + ".img" if not name.endswith(".img") else name
    with tempfile.NamedTemporaryFile("w", suffix=".txt") as fp:
        fp.write("\n".join(nfiles))
        fp.seek(0)

        # Compose the gmt command
        cmd = [
            gmap_tool, "-j", "-o", os.path.join(input_dir, outname), "-@", fp.name
        ]
        print(f"🖥️ CMD: {' '.join(cmd)}")
        if click.confirm("\n👉️ Continue with the above command? "):
            print(f"📦️ Writing final map .img file: '{outname}'")
            subprocess.run(cmd)


if __name__ == "__main__":
    cli()
