"""Beginner-friendly text preprocessing pipeline using three user inputs."""

import re
import string

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag


def download_nltk_resources():
    """Download the small NLTK data files needed by this program."""
    resources = {
        "tokenizers/punkt": "punkt",
        "tokenizers/punkt_tab": "punkt_tab",
        "corpora/stopwords": "stopwords",
        "corpora/wordnet": "wordnet",
        "taggers/averaged_perceptron_tagger_eng": "averaged_perceptron_tagger_eng",
    }
    for resource_path, resource_name in resources.items():
        try:
            nltk.data.find(resource_path)
        except LookupError:
            nltk.download(resource_name, quiet=True)


def get_wordnet_part_of_speech(tag):
    """Convert a Penn Treebank tag into a WordNet lemmatizer tag."""
    if tag.startswith("J"):
        return "a"  # adjective
    if tag.startswith("V"):
        return "v"  # verb
    if tag.startswith("N"):
        return "n"  # noun
    if tag.startswith("R"):
        return "r"  # adverb
    return "n"


def preprocess_text(text, remove_stopwords=True, lemmatize=True):
    """Clean and tokenize one sentence using the requested options."""
    # Lowercase first, then remove URLs and email addresses completely.
    text = text.lower()
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b", " ", text)

    # Remove punctuation/special characters while keeping letters and digits.
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    tokens = word_tokenize(text)

    english_stopwords = set(stopwords.words("english"))
    if remove_stopwords:
        tokens = [token for token in tokens if token not in english_stopwords]

    if lemmatize:
        lemmatizer = WordNetLemmatizer()
        tagged_tokens = pos_tag(tokens)
        tokens = [
            lemmatizer.lemmatize(token, get_wordnet_part_of_speech(tag))
            for token, tag in tagged_tokens
        ]

    return " ".join(tokens)


def meaningful_token_score(processed_text):
    """Count content words; stopwords do not inflate the comparison score."""
    english_stopwords = set(stopwords.words("english"))
    tokens = processed_text.split()
    return sum(token not in english_stopwords for token in tokens)


def main():
    download_nltk_resources()
    print("TEXT PREPROCESSING PIPELINE")
    print("Enter three messy sentences. URLs and email addresses will be removed.\n")
    texts = [input(f"Enter sentence {number}: ").strip() for number in range(1, 4)]

    configurations = [
        ("Stop OFF | Lemma OFF", False, False),
        ("Stop ON  | Lemma OFF", True, False),
        ("Stop OFF | Lemma ON ", False, True),
        ("Stop ON  | Lemma ON ", True, True),
    ]
    results = {}

    for text_number, text in enumerate(texts, start=1):
        print(f"\n{'=' * 90}\nSentence {text_number}: {text}\n{'=' * 90}")
        for name, remove_stopwords, lemmatize in configurations:
            result = preprocess_text(text, remove_stopwords, lemmatize)
            score = meaningful_token_score(result)
            results.setdefault(name, []).append((result, score))
            print(f"{name}: {result or '[no tokens]'}")
            print(f"  meaningful-token score: {score}")

    # Coverage is measured against the unfiltered output, so deleting words
    # does not automatically produce a better score.
    totals = {name: sum(score for _, score in values) for name, values in results.items()}
    best_score = max(totals.values())
    best = [name for name, score in totals.items() if score == best_score]
    print(f"\n{'=' * 90}\nBEST CONFIGURATION\n{'=' * 90}")
    print(f"{' or '.join(best)} (total meaningful-token score: {best_score})")
    print("The score counts meaningful content tokens rather than rewarding the shortest output.")
    print("When scores tie, the ON + ON configuration is preferable because it also removes stopwords and normalizes word forms.")


if __name__ == "__main__":
    main()
