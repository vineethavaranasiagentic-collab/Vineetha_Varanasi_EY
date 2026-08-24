"""Commercial Banking Relationship Manager Copilot: N-gram text generation.

Creates a synthetic 5,000+ word banking corpus, reuses Problem 7 preprocessing,
trains bigram/trigram/four-gram models, generates 50-word passages, evaluates
them, and prints an evidence-based comparison.

Install:
    python -m pip install pandas numpy nltk spacy
    python -m spacy download en_core_web_sm
Run:
    python commercial_banking_ngrams.py
"""

from __future__ import annotations

import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import DefaultDict, Iterable

import nltk
import numpy as np
import pandas as pd
from nltk.tokenize import wordpunct_tokenize

# Reuse Problem 7's preprocessing function and its selected configuration.
# Add the repository root because Python places the script's folder, rather
# than the repository root, on sys.path when this file is run directly.
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))
from problem_7_preprocessing_pipeline.preprocessing_pipeline import preprocess_text

RANDOM_SEED = 42
MIN_CORPUS_WORDS = 5_000
GENERATION_LENGTH = 50
SEED_TEXT = "the relationship manager"


def create_corpus() -> str:
    """Create a varied, synthetic commercial-banking corpus over 5,000 words."""
    templates = [
        "The relationship manager reviewed the client financials before the quarterly meeting. Revenue remained stable, but cash flow depended on timely customer collections and disciplined working capital management.",
        "The commercial banking team monitored account behavior, deposit balances, payment activity, and credit utilization to understand the client's operating cycle and changing liquidity needs.",
        "The borrower requested a revolving working capital facility because inventory increased ahead of seasonal demand. The RM reviewed the borrowing base, receivables aging, supplier terms, and repayment capacity.",
        "During covenant monitoring, leverage approached the agreed threshold while EBITDA softened. The credit officer requested updated statements, a management forecast, and a documented remediation plan.",
        "Payment behavior showed several delayed invoices and one returned payment. The RM scheduled a cash-flow discussion, reviewed liquidity headroom, and considered whether temporary financing support was appropriate.",
        "The client meeting focused on treasury management, payment automation, commercial cards, payroll services, and merchant acquiring. Strong transaction growth suggested several cross-selling opportunities.",
        "The client was concerned about service response times and competitor pricing. The RM prepared a retention plan with an executive meeting, clear ownership of open issues, and a regular relationship review.",
        "Industry conditions were mixed as input costs, interest rates, labor shortages, and supply-chain disruption affected margins. The bank assessed concentration risk and prepared downside scenarios.",
        "A next-best-action recommendation should be explainable and tied to observed evidence. The Copilot can summarize CRM notes, highlight early warning signals, and suggest human-reviewed follow-up actions.",
        "The RM compared loan maturities, collateral coverage, debt service capacity, and future capital expenditure. The discussion included refinancing options, pricing expectations, and covenant reporting requirements.",
        "The finance director explained that receivables were growing faster than collections. The bank explored invoice financing, a seasonal revolver, and practical steps to improve the cash conversion cycle.",
        "The client had excess operating deposits but used few treasury products. The RM proposed account reconciliation, ACH services, fraud controls, positive pay, and an integrated online banking experience.",
        "A manufacturing client reported weaker orders and higher raw material costs. The RM reviewed margin sensitivity, customer concentration, inventory turnover, and the potential effect on debt service.",
        "The relationship manager documented meeting actions, responsible owners, expected dates, and unresolved questions. Human approval remained necessary before any external client communication was sent.",
        "Credit risk reporting combined financial statements, account trends, covenant results, payment behavior, and industry information. A consistent evidence trail supported responsible portfolio management.",
    ]
    # 15 templates repeated with controlled business variations produce >5,000 words.
    variations = [
        "The follow-up agenda included a financial update, risk review, product discussion, and agreed next steps.",
        "The account plan emphasized proactive communication, accurate documentation, and a practical response to the client's priorities.",
        "The analysis considered both the immediate request and the longer-term relationship, profitability, resilience, and retention outlook.",
        "The RM recorded the evidence in the CRM and planned a human-reviewed recommendation for the next client interaction.",
        "The team also compared current activity with prior periods to distinguish a temporary change from a meaningful early warning signal.",
    ]
    sections: list[str] = []
    for cycle in range(35):
        for index, template in enumerate(templates):
            sections.append(template + " " + variations[(cycle + index) % len(variations)])
    corpus = " ".join(sections)
    if len(re.findall(r"\b\w+\b", corpus)) < MIN_CORPUS_WORDS:
        raise ValueError(f"Corpus must contain at least {MIN_CORPUS_WORDS} words.")
    return corpus


def preprocess_corpus(corpus: str) -> list[str]:
    """Reuse Problem 7 with stop-word removal disabled to retain grammar."""
    original_count = len(re.findall(r"\b\w+\b", corpus))
    # Put spaces around punctuation before reusing Problem 7. Its punctuation
    # removal intentionally deletes symbols, so "follow-up" could otherwise
    # become the unnatural token "followup".
    corpus = re.sub(r"[^\w\s]", " ", corpus)
    # Problem 7 performs lowercase, URL/email normalization, punctuation removal,
    # tokenization, and optional lemmatization. Grammar is retained here by not
    # removing stop words and not lemmatizing the generation corpus.
    processed = preprocess_text(corpus, remove_stopwords=False, lemmatize=False)
    tokens = wordpunct_tokenize(processed)
    tokens = [token for token in tokens if re.fullmatch(r"[a-z0-9_]+", token)]
    print(f"Original word count: {original_count}")
    print(f"Tokens after preprocessing: {len(tokens)}")
    print(f"Processed token sample: {tokens[:20]}")
    if not tokens:
        raise ValueError("Preprocessing produced an empty token list.")
    return tokens


def build_ngrams(tokens: list[str], n: int) -> tuple[Counter[tuple[str, ...]], DefaultDict[tuple[str, ...], Counter[str]]]:
    """Build frequency counts and context-to-next-word distributions."""
    if len(tokens) < n:
        raise ValueError(f"Cannot build {n}-grams from only {len(tokens)} tokens.")
    frequencies: Counter[tuple[str, ...]] = Counter(tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1))
    next_words: DefaultDict[tuple[str, ...], Counter[str]] = defaultdict(Counter)
    for gram in frequencies:
        next_words[gram[:-1]][gram[-1]] += frequencies[gram]
    return frequencies, next_words


def _choose(counter: Counter[str], rng: random.Random) -> str:
    words, weights = zip(*counter.items())
    return rng.choices(list(words), weights=list(weights), k=1)[0]


def generate_text(tokens: list[str], n: int, seed: str, length: int, rng: random.Random) -> list[str]:
    """Generate exactly length words, backing off to shorter contexts when needed."""
    _, distributions = build_ngrams(tokens, n)
    seed_tokens = seed.lower().split()
    positions = [i for i in range(len(tokens) - len(seed_tokens) + 1) if tokens[i : i + len(seed_tokens)] == seed_tokens]
    if not positions:
        fallback = next((tokens[i : i + min(n - 1, len(tokens))] for i in range(len(tokens))), tokens[: n - 1])
        seed_tokens = list(fallback)
        print(f"Seed '{seed}' was not found; using fallback seed: {' '.join(seed_tokens)}")
    generated = seed_tokens[:length]
    while len(generated) < length:
        next_word: str | None = None
        max_context = min(n - 1, len(generated))
        for context_size in range(max_context, 0, -1):
            context = tuple(generated[-context_size:])
            if context in distributions:
                next_word = _choose(distributions[context], rng)
                break
        if next_word is None:
            next_word = tokens[rng.randrange(len(tokens))]
        generated.append(next_word)
    return generated[:length]


def _ngrams(items: list[str], n: int) -> list[tuple[str, ...]]:
    return [tuple(items[i : i + n]) for i in range(max(0, len(items) - n + 1))]


def calculate_metrics(generated: list[str], source_tokens: list[str], n: int) -> dict[str, float | int | str]:
    """Calculate diversity, repetition, and source n-gram overlap metrics."""
    source_ngrams = set(_ngrams(source_tokens, n))
    generated_n = _ngrams(generated, n)
    source_overlap = sum(gram in source_ngrams for gram in generated_n) / len(generated_n) if generated_n else 0.0
    repeated_ngrams = len(generated_n) - len(set(generated_n))
    repetition = repeated_ngrams / len(generated_n) if generated_n else 0.0
    bigrams, trigrams = _ngrams(generated, 2), _ngrams(generated, 3)
    return {
        "Model": {2: "Bigram", 3: "Trigram", 4: "Four-gram"}[n],
        "N": n,
        "Word count": len(generated),
        "Unique word ratio": len(set(generated)) / len(generated) if generated else 0.0,
        "Distinct-2": len(set(bigrams)) / len(bigrams) if bigrams else 0.0,
        "Distinct-3": len(set(trigrams)) / len(trigrams) if trigrams else 0.0,
        "Source overlap": source_overlap,
        "Repetition score": repetition,
    }


def compare_models(results: pd.DataFrame) -> None:
    """Use metrics to identify likely fluency, copying, and diversity outcomes."""
    print("\nEVALUATION RESULTS")
    print(results.to_string(index=False, formatters={column: "{:.3f}".format for column in results.select_dtypes(include="number").columns if column not in ["N", "Word count"]}))
    # A transparent proxy: local n-gram source overlap and low repetition indicate fluency.
    fluency_scores = results["Source overlap"] * 0.6 + results["Distinct-2"] * 0.2 + results["Distinct-3"] * 0.2 - results["Repetition score"] * 0.3
    most_fluent = results.loc[fluency_scores.idxmax(), "Model"]
    most_copying = results.loc[results["Source overlap"].idxmax(), "Model"]
    most_diverse = results.loc[(results["Distinct-2"] + results["Distinct-3"]).idxmax(), "Model"]
    results["Fluency proxy"] = fluency_scores
    best_balance = results.loc[(results["Fluency proxy"] + results["Unique word ratio"] - results["Source overlap"]).idxmax(), "Model"]
    print("\nFINAL ANALYSIS")
    print(f"1. Most fluent by the calculated local-context proxy: {most_fluent}.")
    print(f"2. Copies the source most closely by source n-gram overlap: {most_copying}.")
    print(f"3. Greatest generated diversity by Distinct-2 plus Distinct-3: {most_diverse}.")
    print(f"4. Best measured balance of fluency, uniqueness, and lower copying: {best_balance}.")
    print("Increasing n usually narrows the available context and can improve local coherence while increasing phrase copying. The actual scores above, rather than a hard-coded conclusion, determine this experiment's outcome.")
    print("For a Relationship Manager Copilot, n-grams are useful for teaching local language patterns and demonstrating reproducible generation, but they do not understand client context. Modern LLM/RAG systems are generally better for coherent banking communications because retrieval can ground responses in current approved records, while controls can enforce accuracy, confidentiality, compliance, and human approval.")


def main() -> None:
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)
    print("COMMERCIAL BANKING N-GRAM TEXT GENERATION")
    print(f"NLTK version: {nltk.__version__}")
    corpus = create_corpus()
    tokens = preprocess_corpus(corpus)
    corpus_word_count = len(re.findall(r"\b\w+\b", corpus))
    print(f"Verified corpus size: {corpus_word_count} words")
    generated_passages: list[list[str]] = []
    metric_rows: list[dict[str, float | int | str]] = []
    for n, label in [(2, "BIGRAM"), (3, "TRIGRAM"), (4, "FOUR-GRAM")]:
        rng = random.Random(RANDOM_SEED)
        passage = generate_text(tokens, n, SEED_TEXT, GENERATION_LENGTH, rng)
        generated_passages.append(passage)
        print(f"\n{label} ({len(passage)} words):\n{' '.join(passage)}")
        metric_rows.append(calculate_metrics(passage, tokens, n))
    results = pd.DataFrame(metric_rows)
    compare_models(results)


if __name__ == "__main__":
    main()
