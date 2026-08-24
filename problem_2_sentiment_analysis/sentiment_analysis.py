"""Compare VADER sentiment before and after stop-word removal."""

import importlib
import subprocess
import sys


def ensure_package(package_name, import_name=None):
    # Install a missing library automatically so beginners can run the script.
    """Install a package automatically when it is not available."""
    import_name = import_name or package_name
    try:
        importlib.import_module(import_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])


# Install the two required third-party packages if necessary.
ensure_package("nltk")
ensure_package("pandas")

import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer


# Download language data required by stop-word removal and VADER.
nltk.download("stopwords", quiet=True)
nltk.download("vader_lexicon", quiet=True)


sentences = [
    "The relationship with the managers is not stable, but communication remains proactive.",
    "The company never misses a covenant payment, which gives the market confidence.",
    "Customer retention is very strong because the product continuously improves.",
    "The financials are not healthy, and account behaviour creates additional risk.",
    "There are good opportunities in the industry, but the drafting process is not complete.",
]


# Load common English words such as "the", "is", and "and" for filtering.
english_stop_words = set(stopwords.words("english"))

print("=" * 100)
print("STOP-WORD CHECK")
print("=" * 100)
for word in ("not", "never", "very", "but"):
    status = "REMOVED" if word in english_stop_words else "KEPT"
    print(f"{word:>6}: {status}")


analyzer = SentimentIntensityAnalyzer()


def remove_stop_words(sentence):
    """Remove stop words while preserving word order and punctuation."""
    kept_tokens = []
    for token in sentence.split():
        comparison_token = token.lower().strip(".,!?;:'\"()[]{}")
        if comparison_token not in english_stop_words:
            kept_tokens.append(token)
    return " ".join(kept_tokens)


def classify_sentiment(compound_score):
    """Convert VADER's score into Positive, Negative, or Neutral."""
    if compound_score >= 0.05:
        return "Positive"
    if compound_score <= -0.05:
        return "Negative"
    return "Neutral"


# Calculate both sentiment versions programmatically.
records = []
for number, original in enumerate(sentences, start=1):
    without_stop_words = remove_stop_words(original)
    original_score = analyzer.polarity_scores(original)["compound"]
    filtered_score = analyzer.polarity_scores(without_stop_words)["compound"]
    original_sentiment = classify_sentiment(original_score)
    filtered_sentiment = classify_sentiment(filtered_score)

    records.append({
        "Sentence Number": number,
        "Original Sentence": original,
        "Original Sentiment Score": original_score,
        "Original Sentiment": original_sentiment,
        "Sentence Without Stop Words": without_stop_words,
        "Sentiment Score Without Stop Words": filtered_score,
        "Sentiment Without Stop Words": filtered_sentiment,
        "Meaning Flipped?": "Yes" if original_sentiment != filtered_sentiment else "No",
    })


# Display the requested clean pandas table.
results = pd.DataFrame(records)
print("\n" + "=" * 100)
print("SENTIMENT ANALYSIS COMPARISON")
print("=" * 100)
print(results.to_string(
    index=False,
    formatters={
        "Original Sentiment Score": "{:.4f}".format,
        "Sentiment Score Without Stop Words": "{:.4f}".format,
    },
))


# Summarize changed classifications without hard-coding expected results.
flipped = results.loc[results["Meaning Flipped?"] == "Yes", "Sentence Number"].tolist()
print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)
if flipped:
    print("Sentiment classification flipped for sentence number(s): " + ", ".join(map(str, flipped)))
else:
    print("No sentence changed sentiment classification.")
