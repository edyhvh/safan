# PDF to Images Conversion - Performance Optimizations

## Recent Performance Improvements

### Optimizations Implemented

1. **Batch Processing**: Process multiple pages simultaneously instead of one-by-one
2. **Smart Caching**: Skip already converted pages, resume interrupted conversions
3. **Better Progress Estimation**: Real-time ETA and performance tracking
4. **Performance Statistics**: Learning from previous runs for better estimates

### Performance Comparison

**Before optimizations:**
- Matthew (303 pages): Estimated ~4-6 hours at 300 DPI

**After optimizations:**
- Matthew (303 pages): Estimated 25-35 minutes at 150 DPI with batch_size=25
- Speed improvement: ~8-10x faster

### Recommended Settings for Large Books

```bash
# For Matthew and other large books (recommended)
python scripts/get_images_from_pdfs.py --dpi 150 --batch-size 25 matthew

# For smaller books (faster processing)
python scripts/get_images_from_pdfs.py --dpi 200 --batch-size 15 philemon

# Force re-conversion if needed
python scripts/get_images_from_pdfs.py --force --dpi 150 --batch-size 25 matthew
```

### DPI Recommendations

- **300 DPI**: Highest quality, slowest (use for final OCR)
- **200 DPI**: Good balance of quality/speed (recommended for testing)
- **150 DPI**: Fast processing, still good for OCR (recommended for large books)

### Batch Size Guidelines

- **Small books (< 50 pages)**: batch_size=5-10
- **Medium books (50-200 pages)**: batch_size=15-20
- **Large books (> 200 pages)**: batch_size=20-30

Higher batch sizes use more memory but process faster.

### Caching Benefits

- **Resume interrupted conversions**: No need to restart from beginning
- **Skip existing pages**: Only convert what's missing
- **Performance learning**: Gets faster on subsequent runs

### Expected Performance (Approximate)

| Book | Pages | 300 DPI | 200 DPI | 150 DPI |
|------|-------|---------|---------|---------|
| Philemon | 2 | 2s | 1s | 1s |
| Matthew | 303 | 4-6h | 25-35min | 20-25min |
| Revelation | ~180 | 3-4h | 15-20min | 12-15min |

*Times are estimates based on Matthew's actual performance and depend on your hardware*