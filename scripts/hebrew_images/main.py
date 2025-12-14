#!/usr/bin/env python3
"""
Script to extract Hebrew text columns from biblical manuscript images using dynamic OpenCV detection.

This script processes images, detects the central Hebrew text column (including title),
and crops them dynamically. It handles variations in page layout and falls back to
approximate coordinates if detection fails.

Usage:
    python -m scripts.hebrew_images.main --input-dir data/images/philemon --output-dir data/temp/philemon
"""

import argparse
import logging
from pathlib import Path

from .extractor import HebrewTextExtractor
from .logger import setup_logging

# Setup logging
logger = setup_logging(verbose=False)


def main():
    parser = argparse.ArgumentParser(
        description="Extract Hebrew text columns from images."
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        default="data/images/philemon",
        help="Directory containing input images",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/temp/philemon",
        help="Directory to save cropped images",
    )

    args = parser.parse_args()

    input_path = Path(args.input_dir)
    output_path = Path(args.output_dir)

    logger.info(f"Input Directory: {input_path}")
    logger.info(f"Output Directory: {output_path}")

    extractor = HebrewTextExtractor(input_path, output_path)
    extractor.process_all_images()


if __name__ == "__main__":
    main()
