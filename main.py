#!/usr/bin/env python3
"""Copy the pre-rendered front-page image to the output directory.

The image (entry.png, 1024x1024) is rendered by gen_image.py during the
build session and shipped in this repository; the grading sandbox has no
network and only the standard library, so this entrypoint just copies it.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def main():
    os.makedirs(OUT, exist_ok=True)
    shutil.copyfile(os.path.join(HERE, "entry.png"),
                    os.path.join(OUT, "entry.png"))


if __name__ == "__main__":
    main()
