r"""Simple frequency-based next-word predictor for commercial banking notes.

This is a small educational language model. It uses only the local text corpus,
Python's standard library, and observed word frequencies. It does not use an
LLM, API, pretrained model, or internet search.

Run from the repository root:
    python .\problem_13_next_word_predictor\problem_13.py
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import re


PHRASE_LENGTH = 3  # Change this to use a different number of context words.
CORPUS_FILE = Path(__file__).with_name("banking_corpus.txt")


def preprocess_text(text: str) -> list[str]:
    """Lowercase text, remove punctuation, normalize spaces, and split words."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.split() if text else []


def load_corpus() -> list[list[str]]:
    """Read every banking sentence from banking_corpus.txt."""
    if not CORPUS_FILE.exists():
        raise FileNotFoundError(f"Corpus file not found: {CORPUS_FILE}")
    with CORPUS_FILE.open("r", encoding="utf-8") as file:
        sentences = [preprocess_text(line) for line in file if line.strip()]
    sentences = [sentence for sentence in sentences if sentence]
    if not sentences:
        raise ValueError("The banking corpus is empty.")
    return sentences


def build_frequency_table(sentences: list[list[str]], phrase_length: int) -> dict[tuple[str, ...], Counter[str]]:
    """Map each phrase to counts of the words observed immediately after it."""
    table: dict[tuple[str, ...], Counter[str]] = defaultdict(Counter)
    for words in sentences:
        for index in range(len(words) - phrase_length):
            phrase = tuple(words[index : index + phrase_length])
            next_word = words[index + phrase_length]
            table[phrase][next_word] += 1
    return dict(table)


def predict_next_word(phrase: str, frequency_table: dict[tuple[str, ...], Counter[str]], phrase_length: int):
    """Return the most frequent observed next word and its confidence."""
    words = preprocess_text(phrase)
    key = tuple(words)
    if len(key) != phrase_length or key not in frequency_table:
        return None
    counts = frequency_table[key]
    predicted_word, frequency = counts.most_common(1)[0]
    total = sum(counts.values())
    confidence = frequency / total
    return predicted_word, frequency, total, confidence


def display_frequency_table(frequency_table: dict[tuple[str, ...], Counter[str]]) -> None:
    """Display the learned phrase-to-next-word counts."""
    print("\n" + "=" * 40)
    print("FREQUENCY TABLE")
    print("=" * 40)
    for phrase, counts in sorted(frequency_table.items()):
        print(f"\nPhrase: {' '.join(phrase)}")
        for word, count in counts.most_common():
            print(f"  {word}: {count}")


def main() -> None:
    sentences = load_corpus()
    frequency_table = build_frequency_table(sentences, PHRASE_LENGTH)
    print("=" * 40)
    print("Commercial Banking Next-Word Predictor")
    print("=" * 40)
    print(f"\nTraining corpus loaded: {len(sentences)} sentences")
    print(f"Phrase length: {PHRASE_LENGTH}")
    print("Frequency table created successfully.")
    print("Type 'table' to display the table or 'exit' to quit.")

    while True:
        user_input = input("\nEnter a phrase to predict the next word:\n> ").strip()
        if not user_input:
            print("Please enter a non-empty phrase.")
            continue
        command = user_input.lower()
        if command == "exit":
            print("Program ended.")
            break
        if command == "table":
            display_frequency_table(frequency_table)
            continue

        result = predict_next_word(user_input, frequency_table, PHRASE_LENGTH)
        if result is None:
            print("No prediction available for this phrase.")
            print("Use exactly three words from the banking corpus and try again.")
            continue
        predicted_word, frequency, total, confidence = result
        print(f"\nPredicted next word: {predicted_word}")
        print(f"Frequency: {frequency}")
        print(f"Total occurrences: {total}")
        print(f"Confidence: {confidence:.2%}")
        print("Note: confidence is the observed corpus proportion, not a guarantee.")


if __name__ == "__main__":
    main()
