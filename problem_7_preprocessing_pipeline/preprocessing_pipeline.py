"""Text preprocessing experiment for a banking Relationship Manager Copilot."""

import importlib
import re
import subprocess
import sys


def ensure_package(package_name, import_name=None):
    """Install a package automatically when it is not available."""
    import_name = import_name or package_name
    try:
        importlib.import_module(import_name)
    except ImportError:
        print(f"Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])


# spaCy performs tokenization, stop-word filtering, and lemmatization.
ensure_package("spacy")
import spacy


MODEL_NAME = "en_core_web_sm"
try:
    nlp = spacy.load(MODEL_NAME)
except OSError:
    print(f"Downloading spaCy model {MODEL_NAME}...")
    subprocess.check_call([sys.executable, "-m", "spacy", "download", MODEL_NAME])
    nlp = spacy.load(MODEL_NAME)


# Exactly three messy texts from the Commercial Banking domain.
texts = [
    " Client ABC Holdings BALANCE declined 18%!!! Visit [https://abc.com/financials](https://abc.com/financials) Contact: [RM_TEAM@BANK.COM](mailto:RM_TEAM@BANK.COM) ",
    "Covenant review pending... EBITDA below threshold; borrower delayed payment by 12 DAYS. Email [CFO@CLIENT.COM](mailto:CFO@CLIENT.COM)",
    "Industry NEWS: Manufacturing sector facing higher input COSTS!!! CRM note: client requested working-capital facility -> follow-up ASAP.",
]


def preprocess_text(text, remove_stopwords=False, lemmatize=False):
    """Clean one text and return its final space-separated token string.

    URLs and email addresses are replaced with descriptive tokens rather than
    silently deleted. This preserves the useful fact that contact/link data
    appeared without retaining the actual address.
    """
    # Convert Markdown links such as [label](url) to their URL or email value.
    text = re.sub(r"\[[^\]]*\]\((https?://[^)]+)\)", r" \1 ", text)
    text = re.sub(r"\[[^\]]*\]\((mailto:[^)]+)\)", r" \1 ", text)

    # Replace visible URLs and email addresses with privacy-safe placeholders.
    text = re.sub(r"https?://\S+", " URL_PRESENT ", text, flags=re.IGNORECASE)
    text = re.sub(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", " EMAIL_PRESENT ", text)
    text = re.sub(r"\bmailto:\S+", " EMAIL_PRESENT ", text, flags=re.IGNORECASE)

    # Lowercase and let spaCy tokenize words, numbers, and remaining symbols.
    doc = nlp(text.lower())
    tokens = []
    for token in doc:
        if token.is_space or token.is_punct:
            continue
        if remove_stopwords and token.is_stop:
            continue
        value = token.lemma_ if lemmatize else token.text
        if value and not value.isspace():
            tokens.append(value)

    # Extra whitespace is naturally removed when tokens are joined.
    return " ".join(tokens)


def count_pipeline_features(processed_text):
    """Return simple metrics for comparing each pipeline configuration."""
    tokens = processed_text.split()
    return {
        "Token Count": len(tokens),
        "Unique Token Count": len(set(tokens)),
        # spaCy receives lowercase text, so the placeholders are lowercase too.
        "Contains URL Placeholder": "url_present" in tokens,
        "Contains Email Placeholder": "email_present" in tokens,
    }


def main():
    print("=" * 110)
    print("COMMERCIAL BANKING TEXT PREPROCESSING PIPELINE")
    print("=" * 110)
    print("\nThe URL and email addresses are replaced with safe placeholders.")

    configurations = [
        ("Basic cleaning", False, False),
        ("Stop words removed", True, False),
        ("Stop words + lemmatization", True, True),
    ]

    for number, text in enumerate(texts, start=1):
        print(f"\n{'-' * 110}\nTEXT {number}\n{'-' * 110}")
        print(f"Original: {text.strip()}")
        for name, remove_stopwords, lemmatize in configurations:
            processed = preprocess_text(text, remove_stopwords, lemmatize)
            metrics = count_pipeline_features(processed)
            print(f"\n{name}:\n{processed}")
            print(f"Metrics: {metrics}")

    print("\n" + "=" * 110)
    print("INTERPRETATION")
    print("=" * 110)
    print("Lowercasing makes equivalent words match, such as BALANCE and balance.")
    print("URL_PRESENT and EMAIL_PRESENT preserve evidence of contact/link data without retaining addresses.")
    print("Removing punctuation and extra whitespace makes tokens easier to analyze.")
    print("Stop-word removal reduces common words, while lemmatization maps related forms to a base form.")
    print("For this Copilot, words such as declined, covenant, threshold, delayed, costs, and facility can support risk and follow-up analysis.")


if __name__ == "__main__":
    main()
