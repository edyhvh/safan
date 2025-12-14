# Hebrew Text Column Extractor

A computer vision tool that automatically detects and extracts the central Hebrew text column from biblical manuscript images using OpenCV.

## Overview

This tool processes scanned manuscript pages and dynamically identifies the Hebrew text column (typically the second column from the left), then crops it while preserving important elements like titles and enumeration markers at the top.

## How It Works

### Detection Strategy

The tool uses a **fallback chain** of three detection methods, trying each one until it finds a valid column:

1. **Contour Detection** (Primary)
   - Uses morphological operations to connect text into column-shaped regions
   - Finds all columns and selects the second one from the left
   - Most reliable for clear, well-separated columns

2. **Hough Line Detection** (Fallback)
   - Detects vertical lines that form column boundaries
   - Clusters nearby lines to identify column edges
   - Useful when contour detection fails

3. **Projection-Based Detection** (Last Resort)
   - Analyzes horizontal pixel density (projection) to find dense text regions
   - Uses sliding windows to locate the best column region
   - Works even when other methods struggle

4. **Fallback Coordinates** (Final Safety Net)
   - If all detection methods fail, uses estimated coordinates based on typical page geometry
   - Ensures the tool always produces an output

### Key Features

- **Second Column Selection**: Automatically identifies and extracts the second Hebrew column (not the first)
- **Title Preservation**: Detects and includes title regions at the top of pages
- **Top Alignment**: Always starts from y=0 to preserve enumeration/verse numbers
- **Wide Region Splitting**: If a detected region is too wide (includes multiple columns), it splits to extract just the second column
- **Special Handling**: Custom logic for `john1` manuscript (skips specific images, processes only odd-numbered images from 000009 onwards)
- **Blank Image Detection**: Automatically skips blank or near-blank images

## Installation

Ensure you have the required dependencies:

```bash
pip install opencv-python numpy tqdm
```

## Usage

### Basic Usage

```bash
python -m scripts.hebrew_images.main \
    --input-dir data/images/philemon \
    --output-dir data/temp/philemon
```

### Arguments

- `--input-dir`: Directory containing input images (PNG, JPG, JPEG, TIFF, BMP)
- `--output-dir`: Directory where cropped images will be saved

### Programmatic Usage

```python
from pathlib import Path
from scripts.hebrew_images import HebrewTextExtractor

extractor = HebrewTextExtractor(
    input_dir=Path("data/images/philemon"),
    output_dir=Path("data/temp/philemon")
)
successful, total = extractor.process_all_images()
print(f"Processed {successful}/{total} images")
```

## Architecture

The codebase is organized into focused modules:

```
hebrew_images/
├── __init__.py          # Module exports
├── main.py              # CLI entry point
├── extractor.py         # Main HebrewTextExtractor class
├── detection.py         # Three detection methods
├── validation.py        # Post-detection validation and refinement
├── logger.py            # Improved logging system
└── utils.py             # Shared utilities and constants
```

### Module Responsibilities

- **`extractor.py`**: Main processing logic, image I/O, batch processing
- **`detection.py`**: All three detection algorithms and shared detection helpers
- **`validation.py`**: Post-processing validation and refinement (fixes text cutoff, wrong column selection)
- **`logger.py`**: Organized logging system with per-image summaries
- **`utils.py`**: Constants, fallback coordinates, common utilities (vertical expansion, region splitting, validation)
- **`main.py`**: Command-line interface

## Key Concepts

### Column Geometry

The tool expects Hebrew columns to have specific characteristics:

- **Width**: 800-1200 pixels (typical range)
- **Height**: At least 85% of page height (to capture full text)
- **Position**: Second column from left, typically starting 200-600px from left edge
- **Aspect Ratio**: Tall and narrow (height >> width)

### Detection Flow

```
Image Input
    ↓
Preprocess (grayscale + adaptive threshold)
    ↓
Try Contour Detection
    ↓ (if fails)
Try Hough Line Detection
    ↓ (if fails)
Try Projection Detection
    ↓ (if fails)
Use Fallback Coordinates
    ↓
Validate Box (width, height, position)
    ↓
Detect Title Region (if present)
    ↓
Expand Vertical Range (ensure y=0, full height)
    ↓
Split Wide Regions (if too wide)
    ↓
VALIDATION & REFINEMENT (NEW)
    ├─ Check for text cut off at right edge → Expand width
    ├─ Validate second column selection → Correct if third column detected
    └─ Ensure minimum width
    ↓
Crop and Save
```

### Why Second Column?

Biblical manuscripts typically have:
- **First column**: Often contains other text (Greek, Latin, etc.) or is incomplete
- **Second column**: Contains the main Hebrew text we want to extract
- **Third+ columns**: May contain commentary or other content

The tool specifically targets the second column by:
1. Finding ALL columns in the image
2. Sorting them left-to-right
3. Selecting the one at index 1 (second from left)
4. Validating it's not too close to the left edge (which would be the first column)

### Vertical Expansion

**Critical**: The tool always starts from y=0 (top of image) to preserve:
- Enumeration markers
- Verse numbers
- Title text
- Any content at the very top

Even if detection finds a column starting lower, the tool expands upward to y=0.

### Wide Region Splitting

Sometimes detection methods find a region that's too wide (>900px) because it includes multiple columns. The tool automatically splits these:

1. Identifies if region starts too close to left (<150px) or is too wide
2. Calculates split point (typically ~400-500px from left edge)
3. Extracts the right portion as the second column
4. Ensures minimum width of 800px to avoid cutting text

## Special Cases

### john1 Manuscript

The `john1` directory has special handling:

- **Skips**: Images 000006.png and 000008.png (not part of manuscript)
- **From 000009 onwards**: Processes only odd-numbered images
- **Before 000009**: Processes only even-numbered images (normal behavior)

### Blank Images

Images with very low standard deviation (<15) are considered blank and skipped automatically.

### Odd-Numbered Images

By default, odd-numbered images are skipped (they typically don't contain Hebrew text in this manuscript format).

## Post-Processing Validation

The `validation.py` module automatically fixes common issues:

### Text Cut Off at Right Edge

- **Problem**: Column width is too narrow, cutting off text
- **Solution**: Automatically detects text density at right edge and expands width up to 300px
- **Detection**: Checks last 50px of column for text, then scans beyond for continuation

### Wrong Column Selected (Third Instead of Second)

- **Problem**: Detection algorithm selects third column instead of second
- **Solution**: Validates column position by detecting all columns and comparing overlap
- **Correction**: Automatically adjusts to second column if detected column is too far right (>150px gap)

### Minimum Width Enforcement

- Ensures columns are at least 700px wide (typical Hebrew column width)
- Expands if possible, logs warning if expansion not possible

## Troubleshooting

### Detection Fails Frequently

- Check image quality (resolution, contrast)
- Verify images are properly oriented
- Ensure Hebrew columns are visible and reasonably separated

### Wrong Column Extracted

- The tool targets the second column; if your manuscript has a different layout, you may need to adjust the detection logic
- Check logs for which detection method succeeded
- The validation module should automatically correct third column selections
- Fallback coordinates can be adjusted in `utils.py`

### Images Are Too Wide

- The tool automatically splits wide regions, but if issues persist, check:
  - Image resolution (very high-res images may need different thresholds)
  - Column separation (if columns are too close together, detection may merge them)

### Text Still Cut Off After Processing

- Check validation logs for expansion attempts
- The validation module expands up to 300px; if text extends further, you may need to adjust `max_expand` in `validation.py`
- Very wide columns (>1200px) may need manual review

## Development

### Adding a New Detection Method

1. Add function to `detection.py`:
   ```python
   def find_main_box_from_new_method(thresh: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
       # Your detection logic
       # Return (x, y, w, h) or None
   ```

2. Add to fallback chain in `extractor.py`:
   ```python
   box = find_main_box_from_new_method(thresh)
   ```

### Modifying Detection Parameters

Key constants are in `utils.py`:
- `VERTICAL_WIDTH_RANGE`: Expected column width range
- `VERTICAL_MIN_HEIGHT`: Minimum column height
- `TITLE_SCAN_HEIGHT`: How far down to scan for titles

### Testing

Test with a small subset first:
```bash
# Copy a few test images to a test directory
python -m scripts.hebrew_images.main --input-dir test_images --output-dir test_output
```

## Technical Details

### Image Preprocessing

1. Convert to grayscale
2. Apply Gaussian blur (5x5 kernel)
3. Adaptive thresholding (Gaussian method, 31x31 block, 12 offset)
4. Result: Binary image where text is white and background is black

### Morphological Operations (Contour Method)

- **Horizontal dilation**: Connects characters into words/lines
- **Vertical dilation**: Connects lines into columns
- **Closing**: Fills small gaps

### Validation Criteria

A detected box is considered valid if:
- Width: 600-1400px (flexible range)
- Height: At least 40% of image height or 1500px minimum
- Position: Center before 50% of page width, starts after 50px from left
- Within image bounds

## License

Part of the SAFAN project.
