#!/usr/bin/env python3
"""
SAFAN OCR Example Script
Basic OCR functionality using PaddleOCR and OpenCV
"""

import cv2
import numpy as np
from paddleocr import PaddleOCR
import json
import re
from pathlib import Path

def main():
    print("🔍 SAFAN OCR System Ready")
    print("Available functions:")
    print("- OCR processing with PaddleOCR")
    print("- PDF to image conversion with pdf2image")
    print("- Image processing with OpenCV")
    print("- Text processing with regex and json")

    # Initialize OCR (this will download models on first run)
    try:
        ocr = PaddleOCR(use_angle_cls=True, lang='en')
        print("✅ PaddleOCR initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize PaddleOCR: {e}")
        return

    print("\n🎯 Ready to process images and PDFs!")
    print("Create your OCR scripts in the scripts/ directory")

if __name__ == "__main__":
    main()
