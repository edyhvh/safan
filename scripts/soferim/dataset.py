#!/usr/bin/env python3
"""
Dataset loading and preprocessing for PyTorch Hebrew text correction model.

Loads training pairs from Hutter correction CSVs and Delitzsch corpus,
creates word-level training samples for the Soferim model.
"""

import sys
from pathlib import Path
from torch.utils.data import Dataset, DataLoader, random_split
import json
import csv
import torch

# Add parent directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import our modules
import hebrew_tokens

class SoferimDataset(Dataset):
    """
    Dataset for Hebrew text correction training.

    Combines data from multiple sources:
    - Hutter manual corrections (moriah/lena)
    - Delitzsch corpus (for language modeling)
    """

    def __init__(self, moriah_csv=None, lena_csv=None, delitzsch_dir=None, max_length=64, validation_split=0.1):
        """
        Initialize dataset from multiple sources.

        Args:
            moriah_csv: Path to hutter_moriah.csv
            lena_csv: Path to hutter_lena.csv
            delitzsch_dir: Path to delitzsch JSON files directory
            max_length: Maximum sequence length
            validation_split: Fraction for validation (0.0 to 1.0)
        """
        self.max_length = max_length
        self.validation_split = validation_split

        # Load training pairs from different sources
        self.training_pairs = []
        self.vocab = hebrew_tokens.HebrewWordVocabulary()

        if moriah_csv:
            self._load_moriah_data(moriah_csv)
        if lena_csv:
            self._load_lena_data(lena_csv)
        if delitzsch_dir:
            self._load_delitzsch_data(delitzsch_dir)

        # Build vocabulary from all texts
        all_texts = [pair['original'] for pair in self.training_pairs] + \
                   [pair['corrected'] for pair in self.training_pairs]
        self.vocab.build_vocab(all_texts)

        print(f"Loaded {len(self.training_pairs)} training pairs")
        print(f"Vocabulary size: {len(self.vocab)}")

    def _load_moriah_data(self, csv_path):
        """Load training pairs from Moriah corrections."""
        print(f"Loading Moriah data from {csv_path}...")

        pairs = hebrew_tokens.load_training_pairs_from_csv(csv_path)
        self.training_pairs.extend(pairs)

        print(f"  Added {len(pairs)} Moriah correction pairs")

    def _load_lena_data(self, csv_path):
        """Load training pairs from Lena corrections."""
        print(f"Loading Lena data from {csv_path}...")

        pairs = hebrew_tokens.load_training_pairs_from_csv(csv_path)
        self.training_pairs.extend(pairs)

        print(f"  Added {len(pairs)} Lena correction pairs")

    def _load_delitzsch_data(self, delitzsch_dir):
        """Load Delitzsch corpus for language modeling training."""
        print(f"Loading Delitzsch corpus from {delitzsch_dir}...")

        delitzsch_path = Path(delitzsch_dir)
        json_files = list(delitzsch_path.glob('*.json'))

        verses_loaded = 0

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    book_data = json.load(f)

                # Extract verses from all chapters
                for chapter in book_data['chapters']:
                    for verse in chapter['verses']:
                        vocalized_text = verse['text_nikud'].strip()
                        if vocalized_text:
                            # For Delitzsch, we'll create "correction" pairs where original = corrected
                            # This helps the model learn valid Hebrew patterns
                            self.training_pairs.append({
                                'original': vocalized_text,
                                'corrected': vocalized_text,
                                'source': 'delitzsch',
                                'book': book_data.get('book_name', 'unknown')
                            })
                            verses_loaded += 1

            except Exception as e:
                print(f"    Error processing {json_file}: {e}")
                continue

        print(f"  Added {verses_loaded} Delitzsch verses for language modeling")

    def __len__(self):
        return len(self.training_pairs)

    def __getitem__(self, idx):
        """Get training sample by index."""
        pair = self.training_pairs[idx]

        # Create dataset sample using our tokenization
        correction_dataset = hebrew_tokens.HebrewCorrectionDataset(
            [pair], vocab=self.vocab, max_length=self.max_length
        )

        return correction_dataset[0]

    def get_vocab_size(self):
        """Get vocabulary size."""
        return len(self.vocab)

    def create_data_loaders(self, batch_size=8, shuffle=True):
        """
        Create train/validation data loaders.

        Returns:
            tuple: (train_loader, val_loader) or (data_loader, None)
        """
        if self.validation_split > 0:
            # Split dataset
            val_size = int(len(self) * self.validation_split)
            train_size = len(self) - val_size
            train_dataset, val_dataset = random_split(self, [train_size, val_size])

            train_loader = DataLoader(
                train_dataset,
                batch_size=batch_size,
                shuffle=shuffle,
                collate_fn=self.collate_fn,
                num_workers=0
            )

            val_loader = DataLoader(
                val_dataset,
                batch_size=batch_size,
                shuffle=False,
                collate_fn=self.collate_fn,
                num_workers=0
            )

            return train_loader, val_loader
        else:
            data_loader = DataLoader(
                self,
                batch_size=batch_size,
                shuffle=shuffle,
                collate_fn=self.collate_fn,
                num_workers=0
            )
            return data_loader, None

    def collate_fn(self, batch):
        """
        Collate function for DataLoader.

        Args:
            batch: List of samples

        Returns:
            dict: Batched tensors
        """
        # Use fixed max length for all sequences (not batch max)
        max_len = self.max_length

        # Pad sequences
        input_batch = []
        error_mask_batch = []
        lengths = []

        for sample in batch:
            input_seq = sample['input_tokens'][:max_len]  # Truncate if longer
            error_mask = sample['error_mask'][:max_len]   # Truncate if longer
            length = min(sample['length'], max_len)       # Actual length (capped)

            # Pad to max_len
            padded_input = input_seq + [self.vocab['<pad>']] * (max_len - len(input_seq))
            padded_mask = error_mask + [0] * (max_len - len(error_mask))

            input_batch.append(padded_input)
            error_mask_batch.append(padded_mask)
            lengths.append(length)

        return {
            'input_tokens': torch.tensor(input_batch, dtype=torch.long),
            'error_mask': torch.tensor(error_mask_batch, dtype=torch.long),
            'lengths': torch.tensor(lengths, dtype=torch.long),
            'original_texts': [sample['original_text'] for sample in batch],
            'corrected_texts': [sample['corrected_text'] for sample in batch]
        }

def load_soferim_dataset(project_root=None, validation_split=0.1, batch_size=8, max_length=32):
    """
    Load complete Soferim dataset from project structure.

    Args:
        project_root: Path to project root (auto-detects if None)
        validation_split: Fraction for validation
        batch_size: Batch size for data loading

    Returns:
        tuple: (train_loader, val_loader, vocab_size)
    """
    if project_root is None:
        # Auto-detect project root
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent

    # Define paths
    moriah_csv = project_root / 'data' / 'review' / 'hutter_moriah.csv'
    lena_csv = project_root / 'data' / 'review' / 'hutter_lena.csv'
    delitzsch_dir = project_root / 'data' / 'delitzsch'

    # Check which files exist
    moriah_path = moriah_csv if moriah_csv.exists() else None
    lena_path = lena_csv if lena_csv.exists() else None
    delitzsch_path = delitzsch_dir if delitzsch_dir.exists() else None

    if not any([moriah_path, lena_path, delitzsch_path]):
        raise FileNotFoundError("No training data found. Check paths to CSV files and Delitzsch directory.")

    # Create dataset
    dataset = SoferimDataset(
        moriah_csv=moriah_path,
        lena_csv=lena_path,
        delitzsch_dir=delitzsch_path,
        validation_split=validation_split,
        max_length=max_length
    )

    # Create data loaders
    train_loader, val_loader = dataset.create_data_loaders(batch_size=batch_size)

    return train_loader, val_loader, dataset.get_vocab_size()

def load_delitzsch_only(project_root=None, validation_split=0.1, batch_size=16, max_samples=5000):
    """
    Load only Delitzsch corpus for pretraining.

    Args:
        project_root: Path to project root
        validation_split: Fraction for validation
        batch_size: Batch size
        max_samples: Maximum samples to load

    Returns:
        tuple: (train_loader, val_loader, vocab_size)
    """
    if project_root is None:
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent

    delitzsch_dir = project_root / 'data' / 'delitzsch'

    if not delitzsch_dir.exists():
        raise FileNotFoundError(f"Delitzsch directory not found at {delitzsch_dir}")

    # Create dataset with only Delitzsch data
    dataset = SoferimDataset(
        moriah_csv=None,
        lena_csv=None,
        delitzsch_dir=delitzsch_dir,
        validation_split=validation_split
    )

    # Limit dataset size for faster training
    if max_samples and len(dataset.training_pairs) > max_samples:
        dataset.training_pairs = dataset.training_pairs[:max_samples]
        print(f"Limited Delitzsch dataset to {max_samples} samples")

    # Rebuild vocabulary with limited data
    all_texts = [pair['original'] for pair in dataset.training_pairs] + \
               [pair['corrected'] for pair in dataset.training_pairs]
    dataset.vocab = hebrew_tokens.HebrewWordVocabulary()
    dataset.vocab.build_vocab(all_texts)

    train_loader, val_loader = dataset.create_data_loaders(batch_size=batch_size)

    return train_loader, val_loader, dataset.get_vocab_size()