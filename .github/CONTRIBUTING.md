# Contributing to Shafan 🤝

Thank you for your interest in improving this historical Hebrew text project! Whether you're fixing transcription errors, improving code, or enhancing documentation, your contributions help preserve and make accessible this 426-year-old manuscript.

## Ways to Contribute

### 📖 Text Corrections

Found a transcription error in the Hebrew text? This is the most valuable contribution!

#### Before You Start

**Always verify corrections against the original manuscript images:**
- View images at [Hugging Face: edyhvh/hutter](https://huggingface.co/datasets/edyhvh/hutter)
- Compare the printed text carefully — historical Hebrew can be subtle
- Check nikud (vowel marks) and dagesh (dots) accuracy

#### Report an Error

1. Go to [Issues](https://github.com/edyhvh/shafan/issues)
2. Click **New issue** → Select **"Text Correction"** template
3. Fill in the information:
   - **Book, Chapter, Verse** (e.g., "Matthew 5:3")
   - **Current text** (copy from website)
   - **Corrected text** (what it should be)
   - **Error type** (missing nikud, wrong letter, etc.)
   - **Manuscript verification** (link to the specific image on Hugging Face)
4. Submit!

#### Fix It Yourself

1. **Fork** this repository
2. **Verify** your correction against [manuscript images](https://huggingface.co/datasets/edyhvh/hutter)
3. **Edit** the JSON file in `/output/[book-name].json`
   - Structure: `chapters[chapter-1].verses[verse-1].text_nikud`
   - Example for Matthew 5:3: `output/matthew.json` → `chapters[4].verses[2].text_nikud`
4. **Test locally** (optional):
   ```bash
   cd frontend
   npm run sync-data  # Sync from /output/ to /frontend/public/data/
   npm run dev        # View your changes at localhost:3001
   ```
5. **Commit** with a clear message:
   ```bash
   git commit -m "Fix Matthew 5:3 - corrected nikud on בְּרוּכִים"
   ```
6. **Push** and create a **Pull Request**
7. **Reference** the issue number if applicable: "Fixes #123"

> **Note:** Files in `/frontend/public/data/` are auto-synced from `/output/` during build. Always edit the `/output/` JSON files as the source of truth.

### 💻 Code Contributions

Want to improve the processing pipeline or web interface?

#### Setup Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/shafan.git
cd shafan

# Install dependencies
python setup.py

# For frontend work
cd frontend
npm install
```

#### Code Standards

- **Python**: Follow PEP 8, use type hints where helpful
- **JavaScript/TypeScript**: Follow existing ESLint rules, use npm
- **Commits**: Clear, descriptive messages in English
- **Documentation**: Update relevant README files for significant changes

#### Testing

```bash
# Frontend checks
cd frontend
npm run lint
npm run type-check

# Test your changes locally
npm run dev
```

### 🌐 Translations

We currently support Hebrew, Spanish, and English. Interested in adding:
- Portuguese
- Arabic
- Farsi
- Other languages

Open an issue to discuss the translation strategy before starting work.

### 📚 Documentation

Improvements to README files, inline comments, or new guides are always welcome!

## Pull Request Process

1. **Create a feature branch**: `git checkout -b fix/matthew-5-3-nikud`
2. **Make your changes** with clear, focused commits
3. **Test locally** to ensure nothing breaks
4. **Push** to your fork
5. **Open a PR** with:
   - Clear title describing the change
   - Description of what was changed and why
   - For text corrections: link to manuscript image verification
   - Reference any related issues
6. **Respond to reviews** — maintainers may request changes
7. **Celebrate** when merged! 🎉

## Code Review Process

- All PRs require review by `@edyhvh` (see [CODEOWNERS](.github/CODEOWNERS))
- Automated checks must pass:
  - JSON validation (for text changes)
  - Frontend linting (for code changes)
  - Security scans
- Text corrections will be double-checked against manuscript images
- Code changes should maintain existing architecture patterns

## Types of Errors We Fix

| Error Type | Example | Priority |
|------------|---------|----------|
| **Missing nikud** | שלום → שָׁלוֹם | High |
| **Wrong letter** | אבי → אבא | **Critical** |
| **Dagesh errors** | בית → בִּית | High |
| **Missing words** | Entire word skipped | **Critical** |
| **Wrong cantillation** | Incorrect teamim marks | Medium |
| **Formatting** | Spacing, paragraphs | Low |

## Questions or Need Help?

- 💬 **General questions**: Open a [Discussion](https://github.com/edyhvh/shafan/discussions)
- 🐛 **Found a bug**: Create an [Issue](https://github.com/edyhvh/shafan/issues)
- 🤔 **Not sure where to start**: Comment on an existing issue or reach out to `@edyhvh`

## Community Guidelines

- Be respectful and constructive
- Focus on the work, not the person
- This is a scholarly project — accuracy and sources matter
- English is preferred for code and documentation, but we welcome contributors from all backgrounds

---

**Thank you for helping preserve and share this important historical text! 🙏**

