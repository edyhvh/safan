#!/usr/bin/env python3
"""
Hutter Polyglot Bible PDF Downloader using aria2

Efficient downloader focused on aria2 for maximum speed.
Supports downloading individual books, multiple books, or all books.

Usage:
    python scripts/download_hutter_aria.py all                    # Download all books
    python scripts/download_hutter_aria.py matthew               # Download Matthew only
    python scripts/download_hutter_aria.py matthew mark luke     # Download multiple books
    python scripts/download_hutter_aria.py --list                # List available books
    python scripts/download_hutter_aria.py --test                # Download to data/temp for testing
"""

import argparse
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Base URL for downloads (using HTTP to avoid SSL issues)
BASE_URL = "http://ia601408.us.archive.org/32/items/hutter-polyglot/"

# PDF list embedded in the script (from data/temp/pdf_list.txt, excluding covers)
PDF_FILES = [
    '1-%20Matthew.pdf',
    '2-%20Mark.pdf',
    '3-%20Luke.pdf',
    '4-%20John.pdf',
    '5-%20Acts.pdf',
    '6-%20Romans.pdf',
    '7-%20First%20Corithians.pdf',
    '8-%20Second%20Corinthians.pdf',
    '9%20-%20Galations.pdf',
    '10%20-%20Ephesians.pdf',
    '11%20-%20Phillipians.pdf',
    '12%20-%20Colossians.pdf',
    '13%20-%201st%20Thessalonians.pdf',
    '14%20-%202nd%20Thessalonians.pdf',
    '15%20-%201st%20Timothy.pdf',
    '16%20-%202nd%20Timothy.pdf',
    '17%20-%20Titus.pdf',
    '18%20-%20Philemon.pdf',
    '19%20-%20Hebrews.pdf',
    '20%20-%20James.pdf',
    '21%20-%201st%20Peter.pdf',
    '22%20-%202nd%20Peter.pdf',
    '23%20-%201st%20John.pdf',
    '24%20-%202nd%20John.pdf',
    '25%20-%203rd%20John.pdf',
    '26%20-%20Jude.pdf',
    '27%20-%20Revelation%20-%20missing%20ch.%209%2017-21.pdf'
]

# Simple English names mapping
BOOK_NAMES = {
    'matthew': '1-%20Matthew.pdf',
    'mark': '2-%20Mark.pdf',
    'luke': '3-%20Luke.pdf',
    'john': '4-%20John.pdf',
    'acts': '5-%20Acts.pdf',
    'romans': '6-%20Romans.pdf',
    'corinthians1': '7-%20First%20Corithians.pdf',
    'corinthians2': '8-%20Second%20Corinthians.pdf',
    'galatians': '9%20-%20Galations.pdf',
    'ephesians': '10%20-%20Ephesians.pdf',
    'philippians': '11%20-%20Phillipians.pdf',
    'colossians': '12%20-%20Colossians.pdf',
    'thessalonians1': '13%20-%201st%20Thessalonians.pdf',
    'thessalonians2': '14%20-%202nd%20Thessalonians.pdf',
    'timothy1': '15%20-%201st%20Timothy.pdf',
    'timothy2': '16%20-%202nd%20Timothy.pdf',
    'titus': '17%20-%20Titus.pdf',
    'philemon': '18%20-%20Philemon.pdf',
    'hebrews': '19%20-%20Hebrews.pdf',
    'james': '20%20-%20James.pdf',
    'peter1': '21%20-%201st%20Peter.pdf',
    'peter2': '22%20-%202nd%20Peter.pdf',
    'john1': '23%20-%201st%20John.pdf',
    'john2': '24%20-%202nd%20John.pdf',
    'john3': '25%20-%203rd%20John.pdf',
    'jude': '26%20-%20Jude.pdf',
    'revelation': '27%20-%20Revelation%20-%20missing%20ch.%209%2017-21.pdf'
}

# Clean output filenames
OUTPUT_NAMES = {
    'matthew': 'matthew.pdf',
    'mark': 'mark.pdf',
    'luke': 'luke.pdf',
    'john': 'john.pdf',
    'acts': 'acts.pdf',
    'romans': 'romans.pdf',
    'corinthians1': 'corinthians1.pdf',
    'corinthians2': 'corinthians2.pdf',
    'galatians': 'galatians.pdf',
    'ephesians': 'ephesians.pdf',
    'philippians': 'philippians.pdf',
    'colossians': 'colossians.pdf',
    'thessalonians1': 'thessalonians1.pdf',
    'thessalonians2': 'thessalonians2.pdf',
    'timothy1': 'timothy1.pdf',
    'timothy2': 'timothy2.pdf',
    'titus': 'titus.pdf',
    'philemon': 'philemon.pdf',
    'hebrews': 'hebrews.pdf',
    'james': 'james.pdf',
    'peter1': 'peter1.pdf',
    'peter2': 'peter2.pdf',
    'john1': 'john1.pdf',
    'john2': 'john2.pdf',
    'john3': 'john3.pdf',
    'jude': 'jude.pdf',
    'revelation': 'revelation.pdf'
}

def is_aria2_available():
    """Check if aria2c is installed and available"""
    return shutil.which('aria2c') is not None

def list_books():
    """List all available books with their simple names"""
    print("Available books:")
    print("=" * 50)
    for book_name in sorted(BOOK_NAMES.keys()):
        print(f"  {book_name}")
    print("\nUsage examples:")
    print("  python scripts/download_hutter_aria.py matthew")
    print("  python scripts/download_hutter_aria.py matthew mark luke john")
    print("  python scripts/download_hutter_aria.py all")

def validate_books(book_names):
    """Validate that requested books exist"""
    invalid_books = []
    valid_books = []

    for book in book_names:
        if book.lower() == 'all':
            return list(BOOK_NAMES.keys())
        elif book.lower() in BOOK_NAMES:
            valid_books.append(book.lower())
        else:
            invalid_books.append(book)

    if invalid_books:
        print(f"Error: Unknown books: {', '.join(invalid_books)}")
        print("Use --list to see available books")
        sys.exit(1)

    return valid_books

def download_books(book_names, output_dir, force_redownload=False, resume_existing=False,
                  connections_per_file=16, max_concurrent=5):
    """
    Download books using aria2c

    Args:
        book_names: List of book names to download
        output_dir: Output directory
        force_redownload: Force re-download existing files
        resume_existing: Resume downloads of existing files (treat as incomplete)
        connections_per_file: Number of connections per file
        max_concurrent: Number of concurrent downloads
    """

    if not is_aria2_available():
        print("Error: aria2c is not installed!")
        print("\nInstall aria2:")
        print("  macOS:         brew install aria2")
        print("  Ubuntu/Debian: sudo apt install aria2")
        print("  Windows:       choco install aria2")
        sys.exit(1)

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Filter out existing files if not forcing redownload or resuming
    files_to_download = []
    skipped = 0

    for book_name in book_names:
        filename = BOOK_NAMES[book_name]
        output_name = OUTPUT_NAMES[book_name]
        file_path = os.path.join(output_dir, output_name)

        if os.path.exists(file_path) and not force_redownload and not resume_existing:
            if os.path.getsize(file_path) > 0:
                logger.info(f"Skipping {output_name} (already exists)")
                skipped += 1
                continue
        elif os.path.exists(file_path) and resume_existing and not force_redownload:
            if os.path.getsize(file_path) > 0:
                logger.info(f"Resuming download of {output_name} (existing file)")
            else:
                logger.info(f"Starting download of {output_name}")

        files_to_download.append((filename, output_name))

    if not files_to_download:
        logger.info("All requested files already exist!")
        return True

    action = "Resuming" if resume_existing else "Downloading"
    logger.info(f"{action} {len(files_to_download)} files (skipped {skipped} existing)")

    # Create aria2c input file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        input_file = f.name
        for filename, output_name in files_to_download:
            url = BASE_URL + filename
            f.write(f"{url}\n")
            f.write(f"  out={output_name}\n")

    try:
        # Build aria2c command with optimized settings
        cmd = [
            'aria2c',
            '--input-file', input_file,
            '--dir', output_dir,
            '--max-connection-per-server', str(connections_per_file),
            '--split', str(connections_per_file),
            '--max-concurrent-downloads', str(max_concurrent),
            '--min-split-size', '1M',
            '--continue=true',
            '--auto-file-renaming=false',
            '--allow-overwrite=true' if force_redownload else '--allow-overwrite=false',
            '--console-log-level=notice',
            '--summary-interval=5',
            '--download-result=full',
            '--retry-wait=2',
            '--max-tries=5',
            '--timeout=60',
            '--connect-timeout=30',
            '--lowest-speed-limit=1K',  # Stop if speed drops below 1KB/s
            '--max-file-not-found=3',
            '--remote-time=true',  # Preserve file timestamps
            '--check-certificate=false',  # Skip SSL certificate verification
            '--check-certificate=false',  # Additional SSL skip for some aria2 versions
        ]

        logger.info(f"Starting aria2c with {connections_per_file} connections/file, {max_concurrent} concurrent downloads")
        logger.info(f"Output directory: {output_dir}")
        logger.info("Aria2c will show detailed progress for each file...")

        # Run aria2c
        result = subprocess.run(cmd, capture_output=False)

        if result.returncode == 0:
            logger.info("All downloads completed successfully!")
            return True
        else:
            # Check which files were actually downloaded
            successful = skipped
            failed = []

            for filename, output_name in files_to_download:
                file_path = os.path.join(output_dir, output_name)
                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    successful += 1
                else:
                    failed.append(output_name)

            if failed:
                logger.error(f"Failed downloads: {', '.join(failed)}")
                logger.info(f"Total: {successful} successful, {len(failed)} failed")
                return False
            else:
                logger.info(f"All downloads completed! ({successful} files)")
                return True

    finally:
        # Clean up temp file
        try:
            os.unlink(input_file)
        except OSError:
            pass

def main():
    parser = argparse.ArgumentParser(
        description="Download Hutter Polyglot Bible PDFs using aria2",
        epilog="""
Examples:
  python scripts/download_hutter_aria.py --list                    # List all books
  python scripts/download_hutter_aria.py matthew                  # Download Matthew
  python scripts/download_hutter_aria.py matthew mark luke        # Download multiple books
  python scripts/download_hutter_aria.py all                      # Download all books
  python scripts/download_hutter_aria.py --test matthew mark      # Download to data/temp for testing
  python scripts/download_hutter_aria.py --force matthew          # Force re-download
  python scripts/download_hutter_aria.py --resume matthew         # Resume incomplete downloads
  python scripts/download_hutter_aria.py -c 32 -j 10 matthew      # Custom aria2 settings
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'books',
        nargs='*',
        help='Book names to download (or "all" for all books)'
    )

    parser.add_argument(
        '--output', '-o',
        default='data/source',
        help='Output directory (default: data/source)'
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Download to data/temp for testing'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available books'
    )

    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Force re-download even if files exist'
    )

    parser.add_argument(
        '--resume', '-r',
        action='store_true',
        help='Resume downloads of existing files (treat as incomplete)'
    )

    parser.add_argument(
        '--connections', '-c',
        type=int,
        default=16,
        help='Connections per file (default: 16)'
    )

    parser.add_argument(
        '--concurrent', '-j',
        type=int,
        default=5,
        help='Concurrent downloads (default: 5)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Handle list command
    if args.list:
        list_books()
        return

    # Handle test mode
    output_dir = args.output
    if args.test:
        output_dir = 'data/temp'
        logger.info("Test mode: downloading to data/temp")

    # Validate and get books to download
    if not args.books:
        print("Error: No books specified. Use --list to see available books.")
        print("Example: python scripts/download_hutter_aria.py matthew")
        sys.exit(1)

    book_names = validate_books(args.books)

    # Download books
    success = download_books(
        book_names=book_names,
        output_dir=output_dir,
        force_redownload=args.force,
        resume_existing=args.resume,
        connections_per_file=args.connections,
        max_concurrent=args.concurrent
    )

    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()