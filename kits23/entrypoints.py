"""Functions called by command-line entrypoints"""

from pathlib import Path
from argparse import ArgumentParser
import os

from kits23.download import download_dataset


def download_data_entrypoint():
    """Command-line entrypoint for downloading KiTS23 data

    Respects KITS23_DATASET_PATH environment variable if set.
    Otherwise uses current working directory + dataset/kits23/
    """
    parser = ArgumentParser(description="Download the KiTS23 dataset")
    parser.add_argument(
        "--destination",
        "-d",
        type=str,
        default=None,
        help="Destination path for the dataset (overrides KITS23_DATASET_PATH env var)",
    )
    args = parser.parse_args()

    destination = None
    if args.destination:
        destination = Path(args.destination)
    elif "KITS23_DATASET_PATH" in os.environ:
        destination = Path(os.environ["KITS23_DATASET_PATH"])
    else:
        destination = Path.cwd() / "dataset" / "kits23"

    download_dataset(destination)


# Evaluation entrypoint was moved to evaluation/entry_point.py
