#!/usr/bin/env python3
"""Entrypoint for the news-image-20261122 entry.

The front-page artwork for this entry is rendered ahead of time by
gen_image.py and ships in the repository as entry.png. The grading
sandbox has no network access and only the Python standard library,
so this entrypoint does the one job left to do at run time: place the
pre-rendered image where the grader expects to find it.

It copies entry.png (kept next to this file) into the directory named
by the MAKEFUN_OUTPUT_DIR environment variable, defaulting to
/output, creating that directory first if it does not exist yet.
"""

import os
import shutil
import sys

IMAGE_NAME = "entry.png"
DEFAULT_OUTPUT_DIR = "/output"


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, IMAGE_NAME)
    if not os.path.isfile(source):
        print(f"error: {IMAGE_NAME} not found next to main.py", file=sys.stderr)
        return 1

    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", DEFAULT_OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)

    destination = os.path.join(output_dir, IMAGE_NAME)
    shutil.copyfile(source, destination)
    print(f"wrote {destination}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
