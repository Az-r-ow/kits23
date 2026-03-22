"""A script to download the KiTS23 dataset into this repository"""

import sys
import os
from tqdm import tqdm
from pathlib import Path
import urllib.request
import shutil
from time import sleep

from kits23 import TRAINING_CASE_NUMBERS


# Use environment variable if set, otherwise use current working directory
# This allows the dataset to be placed at the project level instead of in the submodule
if "KITS23_DATASET_PATH" in os.environ:
    DST_PTH = Path(os.environ["KITS23_DATASET_PATH"]).resolve()
else:
    DST_PTH = Path.cwd() / "dataset" / "kits23"


def get_destination(case_id: str, create: bool = False):
    destination = DST_PTH / case_id / "imaging.nii.gz"
    if create:
        destination.parent.mkdir(exist_ok=True)
    return destination


def cleanup(tmp_pth: Path, e: Exception):
    if tmp_pth.exists():
        tmp_pth.unlink()

    if e is None:
        print("\nInterrupted.\n")
        sys.exit()
    raise (e)


def download_case(case_num: int, pbar: tqdm, retry=True):
    remote_name = f"master_{case_num:05d}.nii.gz"
    url = f"https://kits19.sfo2.digitaloceanspaces.com/{remote_name}"
    destination = get_destination(f"case_{case_num:05d}", True)
    tmp_pth = destination.parent / f".partial.{destination.name}"
    try:
        urllib.request.urlretrieve(url, str(tmp_pth))
        shutil.move(str(tmp_pth), str(destination))
    except KeyboardInterrupt as e:
        pbar.close()
        while True:
            try:
                sleep(0.1)
                cleanup(tmp_pth, None)
            except KeyboardInterrupt:
                pass
    except Exception as e:
        if retry:
            print(f"\nFailed to download case_{case_num:05d}. Retrying...")
            sleep(5)
            download_case(case_num, pbar, retry=False)
        pbar.close()
        while True:
            try:
                cleanup(tmp_pth, e)
            except KeyboardInterrupt:
                pass


def download_dataset(destination: Path = None):
    """Download the KiTS23 dataset

    Args:
        destination: Optional destination path. If None, uses DST_PTH global variable
    """
    global DST_PTH
    if destination is not None:
        DST_PTH = Path(destination).resolve()

    # Make output directory if it doesn't exist already
    DST_PTH.mkdir(parents=True, exist_ok=True)

    print(f"\nDownloading KiTS23 dataset to: {DST_PTH}\n")

    # Determine which cases still need to be downloaded
    left_to_download = []
    for case_num in TRAINING_CASE_NUMBERS:
        case_id = f"case_{case_num:05d}"
        dst = get_destination(case_id)
        if not dst.exists():
            left_to_download = left_to_download + [case_num]

    # Show progressbar as cases are downloaded
    print(f"\nFound {len(left_to_download)} cases to download\n")
    for case_num in (pbar := tqdm(left_to_download)):
        pbar.set_description(f"Dowloading case_{case_num:05d}...")
        download_case(case_num, pbar)


if __name__ == "__main__":
    download_dataset()
