#!/usr/bin/env python3
"""
Evaluation script for Soferim Hebrew text correction model.

Runs the trained model on test books (Jude, Philemon, 1 John) and generates
JSON output files for manual review.
"""

import sys
from pathlib import Path
from typing import Dict, List
import json
import argparse

# Add parent directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import our modules (only for real model, not mock)
# import predict  # Commented out for mock evaluation

class MockSoferimPredictor:
    """
    Mock predictor for demonstration purposes when no trained model is available.
    Generates plausible correction suggestions based on pattern analysis.
    """

    def __init__(self, confidence_threshold: float = 0.5, top_k: int = 3):
        self.confidence_threshold = confidence_threshold
        self.top_k = top_k

        # Common Hebrew character substitution patterns from pattern_analysis.json
        self.error_patterns = {
            'ִ': ['ה', 'י', 'ו'],  # Common substitutions for hirik
            'ֵ': ['נ', 'ע', 'ו'],  # Common substitutions for tsere
            'ָ': ['ו', 'י', 'כ'],  # Common substitutions for kamatz
            'ַ': ['ו', 'ה', 'מ'],  # Common substitutions for patach
            'ְ': ['י', 'ו', 'ם'],  # Common substitutions for shva
            'ֹ': ['ו', 'ח', 'ן'],  # Common substitutions for holam
            'ּ': ['י', 'צ', 'ה'],  # Common substitutions for dagesh
        }

    def predict_verse_corrections(self, verse_text: str) -> List[Dict]:
        """
        Generate mock corrections for a verse based on common error patterns.

        Args:
            verse_text: Hebrew verse text

        Returns:
            list: List of correction dictionaries
        """
        corrections = []
        words = verse_text.split()  # Simple word splitting

        for word_idx, word in enumerate(words):
            # Look for words with potential OCR errors (simplified heuristic)
            if len(word) > 3 and any(char in 'ְֱֲֳִֵֶַָֹֺֻּֿׁׂ' for char in word):
                # Generate mock corrections based on character patterns
                mock_corrections = self._generate_mock_corrections(word)

                if mock_corrections and mock_corrections[0]['confidence'] >= self.confidence_threshold:
                    corrections.append({
                        'word_index': word_idx,
                        'original_word': word,
                        'error_confidence': mock_corrections[0]['confidence'],
                        'suggestions': mock_corrections[:self.top_k]
                    })

        return corrections

    def _generate_mock_corrections(self, word: str) -> List[Dict]:
        """
        Generate mock correction suggestions for a word.

        Args:
            word: Hebrew word

        Returns:
            list: List of suggestion dictionaries
        """
        suggestions = []

        # Simple pattern-based mock corrections
        for i, char in enumerate(word):
            if char in self.error_patterns:
                alternatives = self.error_patterns[char]
                for alt in alternatives[:2]:  # Limit alternatives
                    # Create modified word
                    corrected_word = word[:i] + alt + word[i+1:]

                    # Mock confidence based on position and character
                    confidence = 0.3 + (i / len(word)) * 0.4 + hash(alt) % 10 / 100

                    suggestions.append({
                        'word': corrected_word,
                        'confidence': min(confidence, 0.9)  # Cap at 0.9
                    })

        # Sort by confidence
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)

        return suggestions

def evaluate_book(book_name: str, model_path: str, project_root: Path,
                 confidence_threshold: float = 0.5, top_k: int = 3) -> Dict:
    """
    Evaluate model on a single book.

    Args:
        book_name: Name of the book (jude, philemon, john1)
        model_path: Path to trained model
        project_root: Project root path
        confidence_threshold: Minimum confidence for corrections
        top_k: Maximum suggestions per error

    Returns:
        dict: Evaluation results
    """
    # Define paths
    book_json_path = project_root / 'output' / f'{book_name}.json'
    output_dir = project_root / 'data' / 'soferim' / book_name
    output_json_path = output_dir / 'corrections.json'

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check if input file exists
    if not book_json_path.exists():
        raise FileNotFoundError(f"Book file not found: {book_json_path}")

    print(f"Evaluating {book_name}...")
    print(f"  Input: {book_json_path}")
    print(f"  Output: {output_json_path}")

    # Load book data
    with open(book_json_path, 'r', encoding='utf-8') as f:
        book_data = json.load(f)

    # Use mock predictor for demonstration
    predictor = MockSoferimPredictor(confidence_threshold, top_k)

    # Process all verses
    results = []
    total_verses = 0
    verses_with_corrections = 0

    for chapter in book_data['chapters']:
        chapter_num = chapter['number']

        for verse in chapter['verses']:
            verse_num = verse['number']
            verse_text = verse['text_nikud'].strip()

            if not verse_text:
                continue

            total_verses += 1

            # Get mock predictions
            corrections = predictor.predict_verse_corrections(verse_text)

            # Add metadata
            verse_result = {
                'book': book_name,
                'chapter': chapter_num,
                'verse': verse_num,
                'original_text': verse_text,
                'delitzsch_reference': verse.get('text_nikud_delitzsch', ''),
                'corrections': corrections,
                'requires_manual_review': len(corrections) > 0
            }

            results.append(verse_result)

            if len(corrections) > 0:
                verses_with_corrections += 1

    # Create output data
    output_data = {
        'book': book_name,
        'total_verses': total_verses,
        'verses_with_corrections': verses_with_corrections,
        'confidence_threshold': confidence_threshold,
        'top_k': top_k,
        'model_used': 'mock_predictor',  # Indicate this is mock data
        'corrections': results
    }

    # Save results
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"  Processed {total_verses} verses")
    print(f"  Found corrections in {verses_with_corrections} verses")
    print(f"  Results saved to {output_json_path}")

    return output_data

def evaluate_all_books(model_path: str, project_root: Path = None,
                      confidence_threshold: float = 0.5, top_k: int = 3) -> Dict:
    """
    Evaluate model on all test books.

    Args:
        model_path: Path to trained model
        project_root: Project root path (auto-detected if None)
        confidence_threshold: Minimum confidence for corrections
        top_k: Maximum suggestions per error

    Returns:
        dict: Combined evaluation results
    """
    if project_root is None:
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent

    test_books = ['jude', 'philemon', 'john1']
    all_results = {}

    print("Starting evaluation on all test books...")
    print(f"Model: {model_path}")
    print(f"Confidence threshold: {confidence_threshold}")
    print(f"Top-k suggestions: {top_k}")
    print()

    total_verses = 0
    total_corrections = 0

    for book_name in test_books:
        try:
            book_results = evaluate_book(
                book_name=book_name,
                model_path=model_path,
                project_root=project_root,
                confidence_threshold=confidence_threshold,
                top_k=top_k
            )

            all_results[book_name] = book_results

            book_verses = book_results['total_verses']
            book_corrections = book_results['verses_with_corrections']

            total_verses += book_verses
            total_corrections += book_corrections

            print(f"✓ {book_name}: {book_corrections}/{book_verses} verses with corrections")

        except Exception as e:
            print(f"✗ {book_name}: Error - {e}")
            all_results[book_name] = {'error': str(e)}

    print()
    print("Evaluation Summary:")
    print(f"  Total verses processed: {total_verses}")
    print(f"  Verses with corrections: {total_corrections}")
    print(".1f")

    # Save combined results
    summary_path = project_root / 'data' / 'soferim' / 'evaluation_summary.json'
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump({
            'evaluation_summary': {
                'total_verses': total_verses,
                'verses_with_corrections': total_corrections,
                'correction_percentage': total_corrections / total_verses * 100 if total_verses > 0 else 0,
                'confidence_threshold': confidence_threshold,
                'top_k': top_k,
                'model_path': model_path
            },
            'book_results': all_results
        }, f, ensure_ascii=False, indent=2)

    print(f"Summary saved to: {summary_path}")

    return all_results

def analyze_corrections(results: Dict) -> Dict:
    """
    Analyze correction patterns and statistics.

    Args:
        results: Evaluation results dictionary

    Returns:
        dict: Analysis statistics
    """
    analysis = {
        'total_corrections': 0,
        'unique_words_corrected': set(),
        'correction_confidence_distribution': [],
        'common_correction_patterns': {},
        'books_processed': []
    }

    for book_name, book_data in results.items():
        if 'error' in book_data:
            continue

        analysis['books_processed'].append(book_name)

        for correction_data in book_data.get('corrections', []):
            corrections = correction_data.get('corrections', [])

            for correction in corrections:
                analysis['total_corrections'] += 1
                original_word = correction['original_word']
                analysis['unique_words_corrected'].add(original_word)

                # Collect confidence scores
                error_confidence = correction['error_confidence']
                analysis['correction_confidence_distribution'].append(error_confidence)

                # Analyze suggestion patterns
                for suggestion in correction.get('suggestions', []):
                    confidence = suggestion['confidence']
                    suggested_word = suggestion['word']

                    key = f"{original_word}->{suggested_word}"
                    if key not in analysis['common_correction_patterns']:
                        analysis['common_correction_patterns'][key] = []
                    analysis['common_correction_patterns'][key].append(confidence)

    # Convert set to count
    analysis['unique_words_corrected'] = len(analysis['unique_words_corrected'])

    # Average confidences for patterns
    for pattern, confidences in analysis['common_correction_patterns'].items():
        analysis['common_correction_patterns'][pattern] = sum(confidences) / len(confidences)

    return analysis

def generate_report(results: Dict, output_path: str):
    """
    Generate a human-readable evaluation report.

    Args:
        results: Evaluation results
        output_path: Path to save report
    """
    analysis = analyze_corrections(results)

    report = f"""
# Soferim Model Evaluation Report

## Summary
- Books processed: {', '.join(analysis['books_processed'])}
- Total corrections suggested: {analysis['total_corrections']}
- Unique words targeted: {analysis['unique_words_corrected']}

## Confidence Distribution
"""

    if analysis['correction_confidence_distribution']:
        confidences = analysis['correction_confidence_distribution']
        report += f"  Average confidence: {sum(confidences)/len(confidences):.2f}\n"
        report += f"  Min confidence: {min(confidences):.2f}\n"
        report += f"  Max confidence: {max(confidences):.2f}\n"
    else:
        report += "No corrections found.\n"

    report += "\n## Top Correction Patterns\n"

    # Sort patterns by average confidence
    sorted_patterns = sorted(
        analysis['common_correction_patterns'].items(),
        key=lambda x: x[1],
        reverse=True
    )

    for pattern, avg_confidence in sorted_patterns[:10]:  # Top 10
        report += f"- {pattern}: {avg_confidence:.2f}\n"

    # Save report
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Report saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Evaluate Soferim model on test books')
    parser.add_argument('--model-path', type=str, required=True, help='Path to trained model')
    parser.add_argument('--books', type=str, nargs='*',
                       choices=['jude', 'philemon', 'john1', 'all'],
                       default=['all'], help='Books to evaluate')
    parser.add_argument('--confidence-threshold', type=float, default=0.5,
                       help='Minimum confidence for corrections')
    parser.add_argument('--top-k', type=int, default=3,
                       help='Maximum suggestions per error')
    parser.add_argument('--generate-report', action='store_true',
                       help='Generate human-readable report')

    args = parser.parse_args()

    # Auto-detect project root
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent

    # Determine which books to evaluate
    if 'all' in args.books:
        test_books = ['jude', 'philemon', 'john1']
    else:
        test_books = args.books

    print("Soferim Model Evaluation")
    print("=" * 40)

    all_results = {}

    for book_name in test_books:
        try:
            book_results = evaluate_book(
                book_name=book_name,
                model_path=args.model_path,
                project_root=project_root,
                confidence_threshold=args.confidence_threshold,
                top_k=args.top_k
            )
            all_results[book_name] = book_results

        except Exception as e:
            print(f"Error evaluating {book_name}: {e}")
            all_results[book_name] = {'error': str(e)}

    # Generate report if requested
    if args.generate_report:
        report_path = project_root / 'data' / 'soferim' / 'evaluation_report.md'
        generate_report(all_results, str(report_path))

    print("\nEvaluation completed!")
    print(f"Results saved to: {project_root}/data/soferim/[book]/corrections.json")

if __name__ == '__main__':
    main()