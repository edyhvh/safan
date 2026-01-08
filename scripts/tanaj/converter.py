"""
Core conversion logic for Tanaj text extraction.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


def number_to_hebrew_numeral(num: int) -> str:
    """
    Convert a number to Hebrew numeral representation.

    Hebrew numerals use letters with special combinations:
    - 1-9: א-ט
    - 10-19: י + unit (except 15=טו, 16=טז)
    - 20-90: כ, ל, מ, נ, ס, ע, פ, צ + unit
    - 100-400: ק, ר, ש, ת + tens + units
    - 500+: ת + remainder
    """
    if num <= 0:
        return str(num)

    # Use the existing HEBREW_NUMERALS dictionary for numbers 1-50
    # For consistency with Besorah books
    from scripts.text.books import HEBREW_NUMERALS

    if num in HEBREW_NUMERALS:
        return HEBREW_NUMERALS[num]

    # For numbers beyond 50, generate Hebrew numerals
    # Units: א-ט (1-9)
    units = ['', 'א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט']
    # Tens: י, כ, ל, מ, נ, ס, ע, פ, צ (10-90)
    tens = ['', 'י', 'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ']
    # Hundreds: ק, ר, ש, ת (100-400)
    hundreds = ['', 'ק', 'ר', 'ש', 'ת']

    result = ''

    # Handle hundreds (100-400)
    if num >= 100:
        hundreds_digit = num // 100
        if hundreds_digit <= 4:
            result += hundreds[hundreds_digit]
        else:
            # For 500+, use ת (400) + remainder
            result += 'ת'
            remainder = num - 400
            if remainder > 0:
                return result + number_to_hebrew_numeral(remainder)
        num = num % 100

    # Handle tens (20-90)
    if num >= 20:
        tens_digit = num // 10
        result += tens[tens_digit]
        num = num % 10

    # Handle 10-19
    elif num >= 10:
        if num == 15:
            result += 'טו'
        elif num == 16:
            result += 'טז'
        else:
            result += 'י' + units[num - 10]
        num = 0

    # Handle units (1-9)
    if num > 0:
        result += units[num]

    return result


def get_available_books(source_dir: str = "~/davar/data/oe") -> List[str]:
    """Get list of available books from source directory."""
    source_path = Path(source_dir).expanduser()
    if not source_path.exists():
        logger.error(f"Source directory not found: {source_path}")
        return []

    books = []
    for item in source_path.iterdir():
        if item.is_dir() and item.name != 'raw':  # Exclude raw directory
            books.append(item.name)
    return sorted(books)


def load_chapter_data(book_path: Path, chapter_num: int) -> Optional[List[Dict[str, Any]]]:
    """Load chapter data from JSON file."""
    chapter_file = book_path / f"{chapter_num}.json"
    if not chapter_file.exists():
        logger.warning(f"Chapter file not found: {chapter_file}")
        return None

    try:
        with open(chapter_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading chapter {chapter_num} from {chapter_file}: {e}")
        return None


def convert_book(book_name: str, source_dir: str = "~/davar/data/oe", output_dir: str = "output", dry_run: bool = False) -> bool:
    """
    Convert a Tanaj book from source format to Shafan JSON format.

    Args:
        book_name: Name of the book to convert
        source_dir: Source directory containing book data
        output_dir: Output directory for JSON files
        dry_run: If True, only process first 5 chapters

    Returns:
        True if conversion successful, False otherwise
    """
    source_path = Path(source_dir).expanduser()
    book_path = source_path / book_name

    if not book_path.exists():
        logger.error(f"Book directory not found: {book_path}")
        return False

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    output_file = output_path / f"{book_name}.json"

    logger.info(f"Converting book: {book_name}")

    # Find all chapter files
    chapter_files = []
    for i in range(1, 200):  # Reasonable upper limit
        chapter_file = book_path / f"{i}.json"
        if chapter_file.exists():
            chapter_files.append(i)
        else:
            break

    if not chapter_files:
        logger.error(f"No chapter files found for book: {book_name}")
        return False

    if dry_run:
        chapter_files = chapter_files[:5]
        logger.info(f"Dry run: processing first {len(chapter_files)} chapters")

    # Group verses by chapter
    chapter_verses = {}

    for chapter_num in chapter_files:
        logger.info(f"Processing chapter {chapter_num}")

        chapter_data = load_chapter_data(book_path, chapter_num)
        if not chapter_data:
            continue

        verses = []
        for verse_data in chapter_data:
            verse_num = verse_data.get('verse', 0)
            hebrew_text = verse_data.get('hebrew', '')

            if verse_num > 0 and hebrew_text:
                verses.append({
                    "number": verse_num,
                    "text_nikud": hebrew_text  # Keep / separators in stored data
                })

        if verses:
            chapter_verses[chapter_num] = verses

    # Convert to output format
    chapters = []
    for chapter_num in sorted(chapter_verses.keys()):
        verses = chapter_verses[chapter_num]
        # Convert chapter number to Hebrew numeral
        hebrew_letter = number_to_hebrew_numeral(chapter_num)

        chapters.append({
            "hebrew_letter": hebrew_letter,
            "number": chapter_num,
            "verses": verses
        })

    if not chapters:
        logger.error(f"No chapters processed for book: {book_name}")
        return False

    # Create output JSON
    output_data = {
        "book_name": book_name,
        "author": "",
        "publication_year": "",
        "chapters": chapters
    }

    # Debug: check chapters structure
    logger.debug(f"Chapters structure: {type(chapters)}, length: {len(chapters)}")
    if chapters:
        logger.debug(f"First chapter: {chapters[0]}")

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        total_verses = sum(len(ch.get('verses', [])) for ch in chapters)
        logger.info(f"Successfully converted {book_name} ({len(chapters)} chapters, {total_verses} verses)")
        return True
    except Exception as e:
        logger.error(f"Error writing output file {output_file}: {e}")
        logger.error(f"Chapters data: {chapters}")
        return False